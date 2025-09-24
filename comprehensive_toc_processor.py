#!/usr/bin/env python3
"""
Comprehensive TOC Sections Processor
Processes all files in toc_sections directory, extracts text, translates, and saves to new files
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from datetime import datetime

# Try to import translation libraries
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    print("Deep Translator not available. Install with: pip install deep-translator")


class TOCSectionsProcessor:
    """Comprehensive processor for TOC sections"""
    
    def __init__(self, input_dir: str = "toc_sections", output_dir: str = "farsi_toc_sections"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.translator = None
        self.processing_stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None,
            'files_processed': [],
            'files_failed': []
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize translator
        self.init_translator()
    
    def init_translator(self):
        """Initialize translation service"""
        if DEEP_TRANSLATOR_AVAILABLE:
            self.translator = GoogleTranslator(source='en', target='fa')
            print("✅ Deep Translator initialized")
        else:
            print("❌ No translation service available")
    
    def get_all_markdown_files(self) -> List[str]:
        """Get all markdown files from input directory"""
        md_files = []
        
        if not os.path.exists(self.input_dir):
            print(f"❌ Input directory '{self.input_dir}' not found")
            return []
        
        for file in os.listdir(self.input_dir):
            if file.endswith('.md') and not file.startswith('00_'):
                md_files.append(os.path.join(self.input_dir, file))
        
        return sorted(md_files)
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, str]:
        """Extract text content from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract filename without extension
            filename = Path(file_path).stem
            
            # Split into sections
            sections = content.split('## 📄 Content')
            if len(sections) < 2:
                return {
                    'filename': filename,
                    'title': filename.replace('_', ' '),
                    'content': content,
                    'metadata': '',
                    'page': 'Unknown'
                }
            
            # Extract metadata and content
            metadata_section = sections[0]
            content_section = sections[1].strip()
            
            # Extract title
            title_match = re.search(r'^# (.+)$', metadata_section, re.MULTILINE)
            title = title_match.group(1) if title_match else filename.replace('_', ' ')
            
            # Extract page number
            page_match = re.search(r'- \*\*Page\*\*: (\d+)', metadata_section)
            page_num = page_match.group(1) if page_match else 'Unknown'
            
            return {
                'filename': filename,
                'title': title,
                'page': page_num,
                'content': content_section,
                'metadata': metadata_section
            }
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return {
                'filename': Path(file_path).stem,
                'title': 'Error',
                'page': 'Unknown',
                'content': '',
                'metadata': ''
            }
    
    def translate_text(self, text: str, max_retries: int = 3) -> str:
        """Translate text using Deep Translator"""
        if not self.translator or not text.strip():
            return text
        
        for attempt in range(max_retries):
            try:
                # Split text into chunks if too long
                if len(text) > 4000:  # Translation service limit
                    chunks = self.split_text(text, 4000)
                    translated_chunks = []
                    
                    for i, chunk in enumerate(chunks):
                        print(f"    📝 Translating chunk {i+1}/{len(chunks)}...")
                        result = self.translator.translate(chunk)
                        translated_chunks.append(result)
                        time.sleep(0.5)  # Rate limiting
                    
                    return ' '.join(translated_chunks)
                else:
                    result = self.translator.translate(text)
                    return result
                    
            except Exception as e:
                print(f"    ⚠️ Translation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return f"[Translation failed: {e}]"
        
        return text
    
    def split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks respecting sentence boundaries"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def create_farsi_file(self, file_data: Dict, translated_content: str) -> str:
        """Create Farsi markdown file"""
        markdown = []
        
        # Add Farsi header
        markdown.append(f"# {file_data['title']} (فارسی)")
        markdown.append("")
        
        # Add metadata
        markdown.append("## 📋 اطلاعات بخش")
        markdown.append("")
        markdown.append(f"- **عنوان**: {file_data['title']}")
        markdown.append(f"- **صفحه**: {file_data['page']}")
        markdown.append(f"- **فایل اصلی**: {file_data['filename']}.md")
        markdown.append(f"- **منبع**: Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf")
        markdown.append(f"- **تاریخ ترجمه**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown.append("")
        
        # Add original metadata for reference
        markdown.append("## 📄 محتوای اصلی")
        markdown.append("")
        markdown.append(file_data['metadata'])
        markdown.append("")
        
        # Add translated content
        markdown.append("## 📄 محتوای ترجمه شده")
        markdown.append("")
        markdown.append(translated_content)
        
        return '\n'.join(markdown)
    
    def process_single_file(self, file_path: str) -> bool:
        """Process a single markdown file"""
        filename = Path(file_path).name
        print(f"🔄 Processing: {filename}")
        
        try:
            # Extract text
            file_data = self.extract_text_from_file(file_path)
            
            if not file_data['content'].strip():
                print(f"    ⚠️ No content found in {filename}")
                self.processing_stats['skipped'] += 1
                return False
            
            # Show content stats
            word_count = len(file_data['content'].split())
            char_count = len(file_data['content'])
            print(f"    📊 Content: {word_count} words, {char_count} characters")
            
            # Translate content
            print(f"    🌐 Translating to Farsi...")
            translated_content = self.translate_text(file_data['content'])
            
            # Create Farsi markdown
            farsi_content = self.create_farsi_file(file_data, translated_content)
            
            # Save Farsi file
            farsi_filename = f"{file_data['filename']}_farsi.md"
            farsi_path = os.path.join(self.output_dir, farsi_filename)
            
            with open(farsi_path, 'w', encoding='utf-8') as f:
                f.write(farsi_content)
            
            print(f"    ✅ Saved: {farsi_filename}")
            self.processing_stats['files_processed'].append(filename)
            return True
            
        except Exception as e:
            print(f"    ❌ Error processing {filename}: {e}")
            self.processing_stats['files_failed'].append(filename)
            return False
    
    def process_all_files(self, max_files: Optional[int] = None) -> Dict:
        """Process all markdown files in input directory"""
        print(f"🔍 Scanning directory: {self.input_dir}")
        
        md_files = self.get_all_markdown_files()
        
        if not md_files:
            print("❌ No markdown files found!")
            return self.processing_stats
        
        if max_files:
            md_files = md_files[:max_files]
        
        self.processing_stats['total_files'] = len(md_files)
        self.processing_stats['start_time'] = datetime.now()
        
        print(f"📚 Found {len(md_files)} files to process")
        print(f"📁 Output directory: {self.output_dir}")
        print("=" * 60)
        
        for i, file_path in enumerate(md_files, 1):
            print(f"\n[{i}/{len(md_files)}] {Path(file_path).name}")
            
            success = self.process_single_file(file_path)
            
            if success:
                self.processing_stats['processed'] += 1
            else:
                self.processing_stats['failed'] += 1
            
            # Progress update
            progress = (i / len(md_files)) * 100
            print(f"📊 Progress: {progress:.1f}% ({i}/{len(md_files)})")
            
            # Rate limiting between files
            if i < len(md_files):
                time.sleep(1)
        
        self.processing_stats['end_time'] = datetime.now()
        return self.processing_stats
    
    def create_comprehensive_index(self) -> str:
        """Create comprehensive index of all processed files"""
        index_file = os.path.join(self.output_dir, "00_COMPREHENSIVE_FARSI_INDEX.md")
        
        markdown = []
        markdown.append("# 📚 فهرست جامع ترجمه‌های فارسی")
        markdown.append("")
        markdown.append(f"**تاریخ ترجمه**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown.append(f"**منبع**: Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf")
        markdown.append(f"**دایرکتوری ورودی**: {self.input_dir}")
        markdown.append(f"**دایرکتوری خروجی**: {self.output_dir}")
        markdown.append("")
        
        # Find all Farsi files
        farsi_files = []
        for file in os.listdir(self.output_dir):
            if file.endswith('_farsi.md'):
                farsi_files.append(file)
        
        farsi_files.sort()
        
        markdown.append(f"**تعداد فایل‌های ترجمه شده**: {len(farsi_files)}")
        markdown.append("")
        
        # List all files with page numbers
        markdown.append("## 📄 فایل‌های ترجمه شده (بر اساس شماره صفحه)")
        markdown.append("")
        
        for file in farsi_files:
            original_name = file.replace('_farsi.md', '.md')
            # Extract page number from filename
            page_match = re.match(r'^(\d+)_', file)
            page_num = page_match.group(1) if page_match else "Unknown"
            
            markdown.append(f"- **صفحه {page_num}**: [{file}]({file}) (اصل: {original_name})")
        
        markdown.append("")
        markdown.append("## 📊 آمار پردازش")
        markdown.append("")
        markdown.append(f"- **کل فایل‌ها**: {self.processing_stats['total_files']}")
        markdown.append(f"- **ترجمه شده**: {self.processing_stats['processed']}")
        markdown.append(f"- **ناموفق**: {self.processing_stats['failed']}")
        markdown.append(f"- **رد شده**: {self.processing_stats['skipped']}")
        markdown.append(f"- **زمان شروع**: {self.processing_stats['start_time']}")
        markdown.append(f"- **زمان پایان**: {self.processing_stats['end_time']}")
        
        if self.processing_stats['start_time'] and self.processing_stats['end_time']:
            duration = self.processing_stats['end_time'] - self.processing_stats['start_time']
            markdown.append(f"- **مدت زمان**: {duration}")
        
        success_rate = (self.processing_stats['processed'] / self.processing_stats['total_files'] * 100) if self.processing_stats['total_files'] > 0 else 0
        markdown.append(f"- **نرخ موفقیت**: {success_rate:.1f}%")
        
        # Add failed files list
        if self.processing_stats['files_failed']:
            markdown.append("")
            markdown.append("## ❌ فایل‌های ناموفق")
            markdown.append("")
            for file in self.processing_stats['files_failed']:
                markdown.append(f"- {file}")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown))
        
        return index_file
    
    def export_processing_stats(self) -> str:
        """Export processing statistics to JSON"""
        stats_file = os.path.join(self.output_dir, "comprehensive_processing_stats.json")
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.processing_stats, f, indent=2, ensure_ascii=False, default=str)
        
        return stats_file


def main():
    parser = argparse.ArgumentParser(description='Comprehensive TOC Sections Processor')
    parser.add_argument('--input-dir', default='toc_sections', 
                       help='Input directory containing markdown files')
    parser.add_argument('--output-dir', default='farsi_toc_sections', 
                       help='Output directory for Farsi translations')
    parser.add_argument('--max-files', type=int, 
                       help='Maximum number of files to process (for testing)')
    parser.add_argument('--single-file', 
                       help='Process only a single file')
    
    args = parser.parse_args()
    
    if not DEEP_TRANSLATOR_AVAILABLE:
        print("❌ Deep Translator not available. Please install:")
        print("pip install deep-translator")
        return 1
    
    print("🚀 Comprehensive TOC Sections Processor")
    print("=" * 50)
    
    # Create processor
    processor = TOCSectionsProcessor(args.input_dir, args.output_dir)
    
    try:
        if args.single_file:
            # Process single file
            if not os.path.exists(args.single_file):
                print(f"❌ File '{args.single_file}' not found")
                return 1
            
            print(f"📄 Processing single file: {args.single_file}")
            success = processor.process_single_file(args.single_file)
            
            if success:
                print("✅ Processing completed successfully!")
            else:
                print("❌ Processing failed!")
                return 1
        else:
            # Process all files
            stats = processor.process_all_files(args.max_files)
            
            print("\n" + "=" * 60)
            print("📊 COMPREHENSIVE PROCESSING SUMMARY")
            print("=" * 60)
            print(f"Total files: {stats['total_files']}")
            print(f"Processed: {stats['processed']}")
            print(f"Failed: {stats['failed']}")
            print(f"Skipped: {stats['skipped']}")
            
            if stats['total_files'] > 0:
                success_rate = (stats['processed'] / stats['total_files'] * 100)
                print(f"Success rate: {success_rate:.1f}%")
            
            if stats['start_time'] and stats['end_time']:
                duration = stats['end_time'] - stats['start_time']
                print(f"Duration: {duration}")
            
            # Create index and stats
            index_file = processor.create_comprehensive_index()
            stats_file = processor.export_processing_stats()
            
            print(f"\n📁 Files saved in: {args.output_dir}")
            print(f"📋 Index created: {index_file}")
            print(f"📊 Stats exported: {stats_file}")
        
        print("\n✅ Comprehensive processing completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

