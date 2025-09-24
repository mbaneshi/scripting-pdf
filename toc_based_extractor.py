#!/usr/bin/env python3
"""
Table of Contents Based PDF Extractor
Extracts sections based on the table of contents structure from PDF files
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

import fitz  # PyMuPDF


class TOCBasedExtractor:
    """Extract sections based on table of contents"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.text_data = {}
        self.toc_structure = []
        
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
    
    def find_table_of_contents(self) -> Optional[int]:
        """Find the page containing the table of contents"""
        if not self.text_data:
            self.extract_text_by_page()
        
        toc_keywords = [
            'contents', 'table of contents', 'toc', 'index',
            'chapter', 'part', 'section', 'day', 'session'
        ]
        
        for page_num, text in self.text_data.items():
            text_lower = text.lower()
            # Look for pages that contain multiple TOC keywords
            keyword_count = sum(1 for keyword in toc_keywords if keyword in text_lower)
            
            # Also look for page number patterns (e.g., "1", "7", "34")
            page_number_patterns = re.findall(r'\b\d+\b', text)
            
            # If page has multiple keywords and page numbers, likely TOC
            if keyword_count >= 3 and len(page_number_patterns) >= 5:
                return page_num
        
        return None
    
    def parse_table_of_contents(self, toc_page: int) -> List[Dict]:
        """Parse the table of contents to extract structure"""
        if toc_page not in self.text_data:
            return []
        
        toc_text = self.text_data[toc_page]
        lines = toc_text.split('\n')
        
        toc_items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for patterns like "Day One: Session One    7"
            # or "Introduction    1" or "Chapter 1    15"
            
            # Pattern 1: Title followed by page number at end
            match = re.match(r'^(.+?)\s+(\d+)\s*$', line)
            if match:
                title = match.group(1).strip()
                page_num = int(match.group(2))
                toc_items.append({
                    'title': title,
                    'page': page_num,
                    'type': self.classify_section_type(title)
                })
                continue
            
            # Pattern 2: Title with page number in middle
            match = re.match(r'^(.+?)\s+(\d+)\s+(.+)$', line)
            if match:
                title = match.group(1).strip()
                page_num = int(match.group(2))
                toc_items.append({
                    'title': title,
                    'page': page_num,
                    'type': self.classify_section_type(title)
                })
                continue
            
            # Pattern 3: Just page numbers (might be continuation)
            if re.match(r'^\d+\s*$', line):
                continue
            
            # Pattern 4: Lines with dots (like "Introduction .......... 1")
            match = re.match(r'^(.+?)\.+\s*(\d+)\s*$', line)
            if match:
                title = match.group(1).strip()
                page_num = int(match.group(2))
                toc_items.append({
                    'title': title,
                    'page': page_num,
                    'type': self.classify_section_type(title)
                })
                continue
        
        # Clean up and validate TOC items
        cleaned_items = []
        for item in toc_items:
            if item['page'] > 0 and item['page'] <= len(self.doc):
                cleaned_items.append(item)
        
        self.toc_structure = cleaned_items
        return cleaned_items
    
    def classify_section_type(self, title: str) -> str:
        """Classify the type of section based on title"""
        title_lower = title.lower()
        
        if 'introduction' in title_lower:
            return 'Introduction'
        elif 'day' in title_lower and 'session' in title_lower:
            return 'Forum Session'
        elif 'day' in title_lower:
            return 'Day'
        elif 'session' in title_lower:
            return 'Session'
        elif 'interval' in title_lower:
            return 'Interval'
        elif 'chapter' in title_lower:
            return 'Chapter'
        elif 'part' in title_lower:
            return 'Part'
        elif 'conclusion' in title_lower:
            return 'Conclusion'
        elif 'afterword' in title_lower:
            return 'Afterword'
        elif 'references' in title_lower:
            return 'References'
        elif 'index' in title_lower:
            return 'Index'
        elif 'contents' in title_lower:
            return 'Contents'
        elif 'about' in title_lower and 'authors' in title_lower:
            return 'About Authors'
        elif 'praise' in title_lower:
            return 'Praise'
        else:
            return 'Other'
    
    def extract_section_by_toc(self, toc_item: Dict) -> str:
        """Extract content for a section based on TOC item"""
        start_page = toc_item['page']
        
        # Find the end page (next TOC item's page - 1)
        end_page = len(self.doc)  # Default to end of document
        
        current_index = self.toc_structure.index(toc_item)
        if current_index + 1 < len(self.toc_structure):
            next_item = self.toc_structure[current_index + 1]
            end_page = next_item['page'] - 1
        
        # Extract content from start_page to end_page
        content_lines = []
        
        for page_num in range(start_page, end_page + 1):
            if page_num in self.text_data:
                content_lines.append(self.text_data[page_num])
        
        return '\n'.join(content_lines)
    
    def extract_all_sections_by_toc(self, output_dir: str = "toc_extracted_sections") -> List[str]:
        """Extract all sections based on TOC structure"""
        if not self.toc_structure:
            print("No TOC structure found. Run parse_table_of_contents() first.")
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        created_files = []
        
        for toc_item in self.toc_structure:
            # Extract content
            content = self.extract_section_by_toc(toc_item)
            
            # Clean up the content
            content = self.clean_content(content)
            
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', toc_item['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{toc_item['page']:03d}_{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Create markdown content
            markdown_content = self.create_toc_markdown(toc_item, content)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            created_files.append(filepath)
            print(f"Created: {filename} (Page {toc_item['page']}, {len(content.split())} words)")
        
        return created_files
    
    def clean_content(self, content: str) -> str:
        """Clean section content"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_toc_markdown(self, toc_item: Dict, content: str) -> str:
        """Create markdown content for TOC-based section"""
        markdown = []
        
        # Add header
        markdown.append(f"# {toc_item['title']}")
        markdown.append("")
        
        # Add metadata
        markdown.append("## 📋 Section Information")
        markdown.append("")
        markdown.append(f"- **Title**: {toc_item['title']}")
        markdown.append(f"- **Page**: {toc_item['page']}")
        markdown.append(f"- **Type**: {toc_item['type']}")
        markdown.append(f"- **Source**: {Path(self.pdf_path).name}")
        markdown.append("")
        
        # Add content
        markdown.append("## 📄 Content")
        markdown.append("")
        markdown.append(content)
        
        return '\n'.join(markdown)
    
    def create_toc_index(self, output_dir: str = "toc_extracted_sections") -> str:
        """Create index file for TOC-based sections"""
        if not self.toc_structure:
            print("No TOC structure found.")
            return ""
        
        index_file = os.path.join(output_dir, "00_TOC_INDEX.md")
        
        markdown = []
        markdown.append("# 📚 Table of Contents Based Index")
        markdown.append("")
        markdown.append(f"**Source PDF**: {Path(self.pdf_path).name}")
        markdown.append(f"**Total Sections**: {len(self.toc_structure)}")
        markdown.append("")
        
        # Group sections by type
        sections_by_type = {}
        for item in self.toc_structure:
            section_type = item['type']
            if section_type not in sections_by_type:
                sections_by_type[section_type] = []
            sections_by_type[section_type].append(item)
        
        # Create index by type
        for section_type, sections in sections_by_type.items():
            markdown.append(f"## {section_type}")
            markdown.append("")
            
            for section in sorted(sections, key=lambda x: x['page']):
                safe_title = re.sub(r'[^\w\s-]', '', section['title'])
                safe_title = re.sub(r'[-\s]+', '_', safe_title)
                filename = f"{section['page']:03d}_{safe_title}.md"
                
                markdown.append(f"- **Page {section['page']}**: [{section['title']}]({filename})")
            
            markdown.append("")
        
        # Add statistics
        markdown.append("## 📊 Statistics")
        markdown.append("")
        markdown.append(f"- **Total Pages**: {len(self.doc)}")
        markdown.append(f"- **Total Sections**: {len(self.toc_structure)}")
        markdown.append(f"- **Section Types**: {', '.join(sections_by_type.keys())}")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown))
        
        return index_file
    
    def export_toc_structure(self, output_file: str = "toc_structure.json") -> str:
        """Export TOC structure to JSON"""
        if not self.toc_structure:
            print("No TOC structure found.")
            return ""
        
        toc_data = {
            'source_pdf': str(self.pdf_path),
            'total_pages': len(self.doc),
            'toc_sections': self.toc_structure,
            'section_types': list(set(item['type'] for item in self.toc_structure))
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()


def main():
    parser = argparse.ArgumentParser(description='Table of Contents Based PDF Extractor')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output-dir', default='toc_extracted_sections', 
                       help='Output directory for extracted sections')
    parser.add_argument('--toc-page', type=int, 
                       help='Specific page number containing TOC (auto-detect if not provided)')
    parser.add_argument('--list-toc', action='store_true', 
                       help='List parsed TOC structure without extracting')
    parser.add_argument('--export-toc', action='store_true', 
                       help='Export TOC structure to JSON')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found")
        return 1
    
    # Create extractor
    extractor = TOCBasedExtractor(args.pdf_path)
    
    if not extractor.load_pdf():
        return 1
    
    try:
        # Extract text
        print(f"Extracting text from {len(extractor.doc)} pages...")
        extractor.extract_text_by_page()
        
        # Find TOC page
        if args.toc_page:
            toc_page = args.toc_page
            print(f"Using specified TOC page: {toc_page}")
        else:
            print("Auto-detecting table of contents page...")
            toc_page = extractor.find_table_of_contents()
            
        if not toc_page:
            print("Could not find table of contents page!")
            return 1
        
        print(f"Found TOC on page {toc_page}")
        
        # Parse TOC
        print("Parsing table of contents...")
        toc_structure = extractor.parse_table_of_contents(toc_page)
        
        if not toc_structure:
            print("Could not parse table of contents!")
            return 1
        
        print(f"Parsed {len(toc_structure)} TOC items:")
        for item in toc_structure:
            print(f"  Page {item['page']}: {item['title']} ({item['type']})")
        
        if args.list_toc:
            return 0
        
        # Export TOC structure if requested
        if args.export_toc:
            toc_file = extractor.export_toc_structure()
            print(f"TOC structure exported to: {toc_file}")
        
        # Extract sections
        print(f"\nExtracting sections to '{args.output_dir}'...")
        created_files = extractor.extract_all_sections_by_toc(args.output_dir)
        
        print(f"\nCreated {len(created_files)} section files")
        
        # Create index
        index_file = extractor.create_toc_index(args.output_dir)
        print(f"Created index file: {index_file}")
        
        print(f"\nAll files saved in: {args.output_dir}")
        print("✅ TOC-based extraction complete!")
        
    finally:
        extractor.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

