#!/usr/bin/env python3
"""
Intelligent Chapter Extractor
Groups pages into logical chapters based on content analysis
"""

import os
import re
from typing import List, Dict, Tuple, Any
from pathlib import Path

def analyze_page_content(page_text: str) -> Dict[str, Any]:
    """Analyze page content to determine chapter boundaries"""
    
    # Clean text
    clean_text = page_text.strip()
    
    # Detect chapter indicators
    chapter_patterns = [
        r'chapter\s+\d+',
        r'chapter\s+[ivx]+',
        r'part\s+\d+',
        r'section\s+\d+',
        r'^\d+\.',  # Numbered sections
        r'^[ivx]+\.',  # Roman numerals
    ]
    
    is_chapter_start = False
    chapter_title = None
    
    for pattern in chapter_patterns:
        if re.search(pattern, clean_text.lower()):
            is_chapter_start = True
            # Extract title
            lines = clean_text.split('\n')
            for line in lines[:3]:  # Check first 3 lines
                if re.search(pattern, line.lower()):
                    chapter_title = line.strip()
                    break
            break
    
    # Detect content density
    word_count = len(clean_text.split())
    line_count = len([line for line in clean_text.split('\n') if line.strip()])
    
    # Detect dialogue vs prose
    has_dialogue = any(char in clean_text for char in ['"', "'", '—'])
    
    # Detect headers/titles
    has_headers = any(line.isupper() and len(line) > 10 for line in clean_text.split('\n')[:5])
    
    return {
        'is_chapter_start': is_chapter_start,
        'chapter_title': chapter_title,
        'word_count': word_count,
        'line_count': line_count,
        'has_dialogue': has_dialogue,
        'has_headers': has_headers,
        'content_density': word_count / max(line_count, 1),
        'is_empty': word_count < 10
    }

def extract_chapters_from_pages(pages_dir: str = "simple_pages") -> List[Dict[str, Any]]:
    """Extract chapters from individual page files"""
    
    print(f"📚 Extracting chapters from {pages_dir}/")
    
    # Get all page files
    page_files = sorted([f for f in os.listdir(pages_dir) if f.startswith("page_") and f.endswith(".txt")])
    
    if not page_files:
        print("❌ No page files found")
        return []
    
    print(f"📄 Found {len(page_files)} pages")
    
    chapters = []
    current_chapter = {
        'chapter_number': 1,
        'title': 'Introduction',
        'start_page': 1,
        'end_page': 1,
        'pages': [],
        'content': '',
        'page_numbers': []
    }
    
    chapter_number = 1
    
    for page_file in page_files:
        # Extract page number
        page_num = int(page_file.split('_')[1].split('.')[0])
        
        # Read page content
        page_path = os.path.join(pages_dir, page_file)
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                page_text = f.read()
        except Exception as e:
            print(f"❌ Error reading {page_file}: {str(e)}")
            continue
        
        # Analyze page content
        analysis = analyze_page_content(page_text)
        
        # Check if this is a new chapter
        if analysis['is_chapter_start'] and len(current_chapter['pages']) > 0:
            # Save current chapter
            current_chapter['end_page'] = page_num - 1
            chapters.append(current_chapter.copy())
            
            # Start new chapter
            chapter_number += 1
            current_chapter = {
                'chapter_number': chapter_number,
                'title': analysis['chapter_title'] or f'Chapter {chapter_number}',
                'start_page': page_num,
                'end_page': page_num,
                'pages': [],
                'content': '',
                'page_numbers': []
            }
        
        # Add page to current chapter
        current_chapter['pages'].append({
            'page_number': page_num,
            'content': page_text,
            'analysis': analysis
        })
        current_chapter['page_numbers'].append(page_num)
        current_chapter['content'] += page_text + '\n\n'
    
    # Add final chapter
    if current_chapter['pages']:
        current_chapter['end_page'] = current_chapter['pages'][-1]['page_number']
        chapters.append(current_chapter)
    
    print(f"📚 Extracted {len(chapters)} chapters")
    
    # Print chapter summary
    for chapter in chapters:
        print(f"📖 Chapter {chapter['chapter_number']}: {chapter['title']}")
        print(f"   Pages: {chapter['start_page']}-{chapter['end_page']} ({len(chapter['pages'])} pages)")
        print(f"   Content length: {len(chapter['content'])} characters")
        print()
    
    return chapters

def save_chapters_to_files(chapters: List[Dict[str, Any]], output_dir: str = "chapters"):
    """Save chapters to individual files"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"💾 Saving chapters to {output_dir}/")
    
    for chapter in chapters:
        # Save original English chapter
        filename = f"chapter_{chapter['chapter_number']:03d}_original.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== CHAPTER {chapter['chapter_number']}: {chapter['title']} ===\n\n")
            f.write(f"Pages: {chapter['start_page']}-{chapter['end_page']}\n")
            f.write(f"Total pages: {len(chapter['pages'])}\n\n")
            f.write("=" * 60 + "\n\n")
            f.write(chapter['content'])
        
        print(f"✅ Saved: {filename}")
    
    print(f"🎉 All chapters saved to {output_dir}/")

def create_chapter_summary(chapters: List[Dict[str, Any]]) -> str:
    """Create a summary of all chapters"""
    
    summary = "📚 CHAPTER EXTRACTION SUMMARY\n"
    summary += "=" * 50 + "\n\n"
    
    total_pages = sum(len(chapter['pages']) for chapter in chapters)
    total_chapters = len(chapters)
    
    summary += f"📊 Statistics:\n"
    summary += f"   Total chapters: {total_chapters}\n"
    summary += f"   Total pages: {total_pages}\n"
    summary += f"   Average pages per chapter: {total_pages / total_chapters:.1f}\n\n"
    
    summary += "📖 Chapter Details:\n"
    summary += "-" * 30 + "\n"
    
    for chapter in chapters:
        summary += f"Chapter {chapter['chapter_number']}: {chapter['title']}\n"
        summary += f"   Pages: {chapter['start_page']}-{chapter['end_page']} ({len(chapter['pages'])} pages)\n"
        summary += f"   Content: {len(chapter['content'])} characters\n"
        
        # Content analysis
        non_empty_pages = [p for p in chapter['pages'] if not p['analysis']['is_empty']]
        summary += f"   Non-empty pages: {len(non_empty_pages)}\n"
        
        if non_empty_pages:
            avg_words = sum(p['analysis']['word_count'] for p in non_empty_pages) / len(non_empty_pages)
            summary += f"   Average words per page: {avg_words:.0f}\n"
        
        summary += "\n"
    
    return summary

def main():
    """Main function to extract chapters"""
    
    print("🚀 Starting intelligent chapter extraction...")
    
    # Extract chapters
    chapters = extract_chapters_from_pages("simple_pages")
    
    if not chapters:
        print("❌ No chapters extracted")
        return
    
    # Save chapters to files
    save_chapters_to_files(chapters)
    
    # Create summary
    summary = create_chapter_summary(chapters)
    
    # Save summary
    with open("chapter_extraction_summary.txt", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("📋 Summary saved to: chapter_extraction_summary.txt")
    print("\n" + summary)
    
    return chapters

if __name__ == "__main__":
    chapters = main()
