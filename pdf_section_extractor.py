#!/usr/bin/env python3
"""
PDF Section Extractor
Intelligently identifies and extracts sections from PDF files (sessions, chapters, etc.)
and saves them as separate markdown files
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

import fitz  # PyMuPDF


class PDFSectionExtractor:
    """Extract specific sections from PDF files"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.text_data = {}
        self.sections = []
        
    def load_pdf(self) -> bool:
        """Load PDF document"""
        try:
            self.doc = fitz.open(self.pdf_path)
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def extract_text_by_page(self) -> Dict[int, str]:
        """Extract text from each page"""
        if not self.doc:
            raise ValueError("PDF not loaded. Call load_pdf() first.")
        
        text_data = {}
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            text_data[page_num + 1] = text  # 1-indexed pages
        
        self.text_data = text_data
        return text_data
    
    def find_section_patterns(self, patterns: List[str] = None) -> List[Dict]:
        """Find section headers using various patterns"""
        if not self.text_data:
            self.extract_text_by_page()
        
        if patterns is None:
            # Default patterns for common section types
            patterns = [
                # Specific patterns for Speaking Being book
                r'(?i)^\s*(day\s+\w+\s*:\s*session\s+\w+)',
                r'(?i)^\s*(forum\s+day\s+\w+\s*:\s*session\s+\w+)',
                r'(?i)^\s*(day\s+\w+\s*:\s*session\s+\w+\s*interval)',
                r'(?i)^\s*(end\s+of\s+day\s+\w+\s*interval)',
                r'(?i)^\s*(interval\s*:)',
                # General patterns
                r'(?i)^\s*(session\s+\d+)',
                r'(?i)^\s*(chapter\s+\d+)',
                r'(?i)^\s*(part\s+\d+)',
                r'(?i)^\s*(day\s+\d+)',
                r'(?i)^\s*(section\s+\d+)',
                r'(?i)^\s*(lesson\s+\d+)',
                r'(?i)^\s*(module\s+\d+)',
                r'(?i)^\s*(unit\s+\d+)',
                r'(?i)^\s*(week\s+\d+)',
                r'(?i)^\s*(phase\s+\d+)',
                r'(?i)^\s*(stage\s+\d+)',
                r'(?i)^\s*(step\s+\d+)',
                # Book structure patterns
                r'(?i)^\s*(introduction)',
                r'(?i)^\s*(conclusion)',
                r'(?i)^\s*(afterword)',
                r'(?i)^\s*(references)',
                r'(?i)^\s*(index)',
                r'(?i)^\s*(contents)',
                r'(?i)^\s*(about\s+the\s+authors)',
                r'(?i)^\s*(praise\s+for)',
            ]
        
        sections = []
        
        for page_num, text in self.text_data.items():
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        sections.append({
                            'page': page_num,
                            'line': line_num,
                            'title': line,
                            'pattern': pattern,
                            'match': match.group(1) if match.groups() else match.group(0)
                        })
                        break
        
        self.sections = sections
        return sections
    
    def extract_section_content(self, start_page: int, end_page: int = None, 
                              start_line: int = 0, end_line: int = None) -> str:
        """Extract content for a specific section"""
        if not self.text_data:
            self.extract_text_by_page()
        
        if end_page is None:
            end_page = start_page
        
        content_lines = []
        
        for page_num in range(start_page, end_page + 1):
            if page_num not in self.text_data:
                continue
            
            lines = self.text_data[page_num].split('\n')
            
            # Determine line range for this page
            if page_num == start_page:
                start_line_page = start_line
            else:
                start_line_page = 0
            
            if page_num == end_page and end_line is not None:
                end_line_page = end_line
            else:
                end_line_page = len(lines)
            
            # Extract lines for this page
            for line_num in range(start_line_page, end_line_page):
                if line_num < len(lines):
                    content_lines.append(lines[line_num])
        
        return '\n'.join(content_lines)
    
    def extract_sections_to_files(self, output_dir: str = "extracted_sections", 
                                patterns: List[str] = None) -> List[str]:
        """Extract all sections and save them as markdown files"""
        if not self.sections:
            self.find_section_patterns(patterns)
        
        if not self.sections:
            print("No sections found!")
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        created_files = []
        
        # Sort sections by page and line
        sorted_sections = sorted(self.sections, key=lambda x: (x['page'], x['line']))
        
        for i, section in enumerate(sorted_sections):
            # Determine the end of this section
            if i + 1 < len(sorted_sections):
                next_section = sorted_sections[i + 1]
                end_page = next_section['page']
                end_line = next_section['line']
            else:
                # Last section goes to end of document
                end_page = max(self.text_data.keys())
                end_line = None
            
            # Extract content
            content = self.extract_section_content(
                section['page'], end_page, section['line'], end_line
            )
            
            # Clean up the content
            content = self.clean_section_content(content)
            
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', section['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{section['page']:03d}_{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Create markdown content
            markdown_content = self.create_markdown_content(section, content)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            created_files.append(filepath)
            print(f"Created: {filename} (Page {section['page']}, {len(content.split())} words)")
        
        return created_files
    
    def clean_section_content(self, content: str) -> str:
        """Clean and format section content"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_markdown_content(self, section: Dict, content: str) -> str:
        """Create properly formatted markdown content"""
        markdown = []
        
        # Add header
        markdown.append(f"# {section['title']}")
        markdown.append("")
        
        # Add metadata
        markdown.append("## 📋 Section Information")
        markdown.append("")
        markdown.append(f"- **Page**: {section['page']}")
        markdown.append(f"- **Pattern**: `{section['pattern']}`")
        markdown.append(f"- **Match**: {section['match']}")
        markdown.append(f"- **Source**: {Path(self.pdf_path).name}")
        markdown.append("")
        
        # Add content
        markdown.append("## 📄 Content")
        markdown.append("")
        markdown.append(content)
        
        return '\n'.join(markdown)
    
    def find_specific_sections(self, section_type: str) -> List[Dict]:
        """Find sections of a specific type (e.g., 'session', 'chapter')"""
        if not self.sections:
            self.find_section_patterns()
        
        section_type_lower = section_type.lower()
        matching_sections = []
        
        for section in self.sections:
            if section_type_lower in section['title'].lower():
                matching_sections.append(section)
        
        return matching_sections
    
    def extract_sessions_only(self, output_dir: str = "sessions") -> List[str]:
        """Extract only session-based sections"""
        session_patterns = [
            r'(?i)^\s*(session\s+\d+)',
            r'(?i)^\s*(forum\s+day\s+\d+:\s*session\s+\d+)',
            r'(?i)^\s*(day\s+\d+:\s*session\s+\d+)',
        ]
        
        return self.extract_sections_to_files(output_dir, session_patterns)
    
    def extract_chapters_only(self, output_dir: str = "chapters") -> List[str]:
        """Extract only chapter-based sections"""
        chapter_patterns = [
            r'(?i)^\s*(chapter\s+\d+)',
            r'(?i)^\s*(part\s+\d+)',
        ]
        
        return self.extract_sections_to_files(output_dir, chapter_patterns)
    
    def create_section_index(self, output_dir: str = "extracted_sections") -> str:
        """Create an index file listing all extracted sections"""
        if not self.sections:
            self.find_section_patterns()
        
        index_file = os.path.join(output_dir, "00_SECTION_INDEX.md")
        
        markdown = []
        markdown.append("# 📚 Section Index")
        markdown.append("")
        markdown.append(f"**Source PDF**: {Path(self.pdf_path).name}")
        markdown.append(f"**Total Sections Found**: {len(self.sections)}")
        markdown.append("")
        
        # Group sections by type
        section_types = {}
        for section in self.sections:
            section_type = self.get_section_type(section['title'])
            if section_type not in section_types:
                section_types[section_type] = []
            section_types[section_type].append(section)
        
        # Create index by type
        for section_type, sections in section_types.items():
            markdown.append(f"## {section_type.title()}")
            markdown.append("")
            
            for section in sorted(sections, key=lambda x: (x['page'], x['line'])):
                safe_title = re.sub(r'[^\w\s-]', '', section['title'])
                safe_title = re.sub(r'[-\s]+', '_', safe_title)
                filename = f"{section['page']:03d}_{safe_title}.md"
                
                markdown.append(f"- **Page {section['page']}**: [{section['title']}]({filename})")
            
            markdown.append("")
        
        # Add statistics
        markdown.append("## 📊 Statistics")
        markdown.append("")
        markdown.append(f"- **Total Pages**: {max(self.text_data.keys()) if self.text_data else 0}")
        markdown.append(f"- **Total Sections**: {len(self.sections)}")
        markdown.append(f"- **Section Types**: {', '.join(section_types.keys())}")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown))
        
        return index_file
    
    def get_section_type(self, title: str) -> str:
        """Determine the type of section based on title"""
        title_lower = title.lower()
        
        if 'session' in title_lower:
            return 'Sessions'
        elif 'chapter' in title_lower:
            return 'Chapters'
        elif 'part' in title_lower:
            return 'Parts'
        elif 'day' in title_lower:
            return 'Days'
        elif 'interval' in title_lower:
            return 'Intervals'
        elif 'introduction' in title_lower:
            return 'Introduction'
        elif 'conclusion' in title_lower:
            return 'Conclusion'
        elif 'afterword' in title_lower:
            return 'Afterword'
        elif 'references' in title_lower:
            return 'References'
        elif 'index' in title_lower:
            return 'Index'
        else:
            return 'Other'
    
    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()


def main():
    parser = argparse.ArgumentParser(description='PDF Section Extractor')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output-dir', default='extracted_sections', 
                       help='Output directory for extracted sections')
    parser.add_argument('--sessions-only', action='store_true', 
                       help='Extract only session-based sections')
    parser.add_argument('--chapters-only', action='store_true', 
                       help='Extract only chapter-based sections')
    parser.add_argument('--custom-patterns', type=str, 
                       help='Custom regex patterns (comma-separated)')
    parser.add_argument('--list-sections', action='store_true', 
                       help='List found sections without extracting')
    parser.add_argument('--create-index', action='store_true', 
                       help='Create section index file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found")
        return 1
    
    # Create extractor
    extractor = PDFSectionExtractor(args.pdf_path)
    
    if not extractor.load_pdf():
        return 1
    
    try:
        # Extract text
        print(f"Extracting text from {len(extractor.doc)} pages...")
        extractor.extract_text_by_page()
        
        # Find sections
        print("Finding sections...")
        patterns = None
        if args.custom_patterns:
            patterns = [p.strip() for p in args.custom_patterns.split(',')]
        
        sections = extractor.find_section_patterns(patterns)
        
        if not sections:
            print("No sections found!")
            return 1
        
        print(f"Found {len(sections)} sections:")
        for section in sections:
            print(f"  Page {section['page']}: {section['title']}")
        
        if args.list_sections:
            return 0
        
        # Extract sections
        print(f"\nExtracting sections to '{args.output_dir}'...")
        
        if args.sessions_only:
            created_files = extractor.extract_sessions_only(args.output_dir)
        elif args.chapters_only:
            created_files = extractor.extract_chapters_only(args.output_dir)
        else:
            created_files = extractor.extract_sections_to_files(args.output_dir, patterns)
        
        print(f"\nCreated {len(created_files)} section files")
        
        # Create index if requested
        if args.create_index:
            index_file = extractor.create_section_index(args.output_dir)
            print(f"Created index file: {index_file}")
        
        print(f"\nAll files saved in: {args.output_dir}")
        print("✅ Section extraction complete!")
        
    finally:
        extractor.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
