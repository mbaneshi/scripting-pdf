#!/usr/bin/env python3
"""
Specialized Forum Session Extractor
Extracts only the main Forum sessions (Day X: Session Y) from the Speaking Being PDF
"""

import os
import sys
import re
from pathlib import Path
from pdf_section_extractor import PDFSectionExtractor


class ForumSessionExtractor(PDFSectionExtractor):
    """Specialized extractor for Forum sessions only"""
    
    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.forum_sessions = []
    
    def find_forum_sessions(self) -> list:
        """Find only the main Forum sessions"""
        if not self.text_data:
            self.extract_text_by_page()
        
        # Specific patterns for Forum sessions
        session_patterns = [
            r'(?i)^\s*(forum\s+day\s+\w+\s*:\s*session\s+\w+)',
            r'(?i)^\s*(day\s+\w+\s*:\s*session\s+\w+)',
        ]
        
        sessions = []
        
        for page_num, text in self.text_data.items():
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                for pattern in session_patterns:
                    match = re.match(pattern, line)
                    if match:
                        sessions.append({
                            'page': page_num,
                            'line': line_num,
                            'title': line,
                            'pattern': pattern,
                            'match': match.group(1) if match.groups() else match.group(0)
                        })
                        break
        
        self.forum_sessions = sessions
        return sessions
    
    def extract_forum_sessions_to_files(self, output_dir: str = "forum_sessions_clean") -> list:
        """Extract only Forum sessions to clean markdown files"""
        if not self.forum_sessions:
            self.find_forum_sessions()
        
        if not self.forum_sessions:
            print("No Forum sessions found!")
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        created_files = []
        
        # Sort sessions by page and line
        sorted_sessions = sorted(self.forum_sessions, key=lambda x: (x['page'], x['line']))
        
        for i, session in enumerate(sorted_sessions):
            # Determine the end of this session
            if i + 1 < len(sorted_sessions):
                next_session = sorted_sessions[i + 1]
                end_page = next_session['page']
                end_line = next_session['line']
            else:
                # Last session goes to end of document
                end_page = max(self.text_data.keys())
                end_line = None
            
            # Extract content
            content = self.extract_section_content(
                session['page'], end_page, session['line'], end_line
            )
            
            # Clean up the content
            content = self.clean_forum_content(content)
            
            # Create filename
            safe_title = re.sub(r'[^\w\s-]', '', session['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{session['page']:03d}_{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Create markdown content
            markdown_content = self.create_forum_markdown(session, content)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            created_files.append(filepath)
            print(f"Created: {filename} (Page {session['page']}, {len(content.split())} words)")
        
        return created_files
    
    def clean_forum_content(self, content: str) -> str:
        """Clean Forum session content"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def create_forum_markdown(self, session: dict, content: str) -> str:
        """Create clean Forum session markdown"""
        markdown = []
        
        # Add header
        markdown.append(f"# {session['title']}")
        markdown.append("")
        
        # Add metadata
        markdown.append("## 📋 Session Information")
        markdown.append("")
        markdown.append(f"- **Page**: {session['page']}")
        markdown.append(f"- **Source**: {Path(self.pdf_path).name}")
        markdown.append("")
        
        # Add content
        markdown.append("## 📄 Session Content")
        markdown.append("")
        markdown.append(content)
        
        return '\n'.join(markdown)
    
    def create_forum_index(self, output_dir: str = "forum_sessions_clean") -> str:
        """Create index for Forum sessions only"""
        if not self.forum_sessions:
            self.find_forum_sessions()
        
        index_file = os.path.join(output_dir, "00_FORUM_SESSIONS_INDEX.md")
        
        markdown = []
        markdown.append("# 🎯 Forum Sessions Index")
        markdown.append("")
        markdown.append(f"**Source PDF**: {Path(self.pdf_path).name}")
        markdown.append(f"**Total Forum Sessions**: {len(self.forum_sessions)}")
        markdown.append("")
        
        # Group sessions by day
        sessions_by_day = {}
        for session in self.forum_sessions:
            # Extract day from title
            day_match = re.search(r'(?i)day\s+(\w+)', session['title'])
            if day_match:
                day = day_match.group(1)
                if day not in sessions_by_day:
                    sessions_by_day[day] = []
                sessions_by_day[day].append(session)
        
        # Create index by day
        for day in sorted(sessions_by_day.keys(), key=lambda x: ['one', 'two', 'three', 'four'].index(x.lower()) if x.lower() in ['one', 'two', 'three', 'four'] else 999):
            markdown.append(f"## Day {day.title()}")
            markdown.append("")
            
            for session in sorted(sessions_by_day[day], key=lambda x: (x['page'], x['line'])):
                safe_title = re.sub(r'[^\w\s-]', '', session['title'])
                safe_title = re.sub(r'[-\s]+', '_', safe_title)
                filename = f"{session['page']:03d}_{safe_title}.md"
                
                markdown.append(f"- **Page {session['page']}**: [{session['title']}]({filename})")
            
            markdown.append("")
        
        # Add statistics
        markdown.append("## 📊 Statistics")
        markdown.append("")
        markdown.append(f"- **Total Pages**: {max(self.text_data.keys()) if self.text_data else 0}")
        markdown.append(f"- **Total Forum Sessions**: {len(self.forum_sessions)}")
        markdown.append(f"- **Days Covered**: {len(sessions_by_day)}")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown))
        
        return index_file


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Forum Session Extractor')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output-dir', default='forum_sessions_clean', 
                       help='Output directory for extracted sessions')
    parser.add_argument('--list-sessions', action='store_true', 
                       help='List found Forum sessions without extracting')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found")
        return 1
    
    # Create extractor
    extractor = ForumSessionExtractor(args.pdf_path)
    
    if not extractor.load_pdf():
        return 1
    
    try:
        # Extract text
        print(f"Extracting text from {len(extractor.doc)} pages...")
        extractor.extract_text_by_page()
        
        # Find Forum sessions
        print("Finding Forum sessions...")
        sessions = extractor.find_forum_sessions()
        
        if not sessions:
            print("No Forum sessions found!")
            return 1
        
        print(f"Found {len(sessions)} Forum sessions:")
        for session in sessions:
            print(f"  Page {session['page']}: {session['title']}")
        
        if args.list_sessions:
            return 0
        
        # Extract sessions
        print(f"\nExtracting Forum sessions to '{args.output_dir}'...")
        created_files = extractor.extract_forum_sessions_to_files(args.output_dir)
        
        print(f"\nCreated {len(created_files)} Forum session files")
        
        # Create index
        index_file = extractor.create_forum_index(args.output_dir)
        print(f"Created index file: {index_file}")
        
        print(f"\nAll files saved in: {args.output_dir}")
        print("✅ Forum session extraction complete!")
        
    finally:
        extractor.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

