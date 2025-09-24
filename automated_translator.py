#!/usr/bin/env python3
"""
Automated Translation Script
Processes extracted PDF sections and translates them to Farsi
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import requests
from datetime import datetime

# Try to import translation libraries
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    print("Deep Translator not available. Install with: pip install deep-translator")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available. Install with: pip install openai")


class AutomatedTranslator:
    """Automated translation system for PDF sections"""
    
    def __init__(self, input_dir: str, output_dir: str = "farsi_translations"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.translator = None
        self.translation_stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
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
    
    def extract_text_from_markdown(self, file_path: str) -> Dict[str, str]:
        """Extract text content from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections
            sections = content.split('## 📄 Content')
            if len(sections) < 2:
                return {'content': content}
            
            # Extract metadata and content
            metadata_section = sections[0]
            content_section = sections[1].strip()
            
            # Extract title
            title_match = re.search(r'^# (.+)$', metadata_section, re.MULTILINE)
            title = title_match.group(1) if title_match else "Untitled"
            
            # Extract page number
            page_match = re.search(r'- \*\*Page\*\*: (\d+)', metadata_section)
            page_num = page_match.group(1) if page_match else "Unknown"
            
            return {
                'title': title,
                'page': page_num,
                'content': content_section,
                'metadata': metadata_section
            }
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return {'content': '', 'title': 'Error', 'page': 'Unknown'}
    
    def translate_with_deep_translator(self, text: str, max_retries: int = 3) -> str:
        """Translate text using Deep Translator"""
        if not self.translator:
            return text
        
        for attempt in range(max_retries):
            try:
                # Split text into chunks if too long
                if len(text) > 4000:  # Translation service limit
                    chunks = self.split_text(text, 4000)
                    translated_chunks = []
                    
                    for chunk in chunks:
                        result = self.translator.translate(chunk)
                        translated_chunks.append(result)
                        time.sleep(0.5)  # Rate limiting
                    
                    return ' '.join(translated_chunks)
                else:
                    result = self.translator.translate(text)
                    return result
                    
            except Exception as e:
                print(f"⚠️ Translation attempt {attempt + 1} failed: {e}")
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
    
    def create_farsi_markdown(self, original_data: Dict, translated_content: str) -> str:
        """Create Farsi markdown file"""
        markdown = []
        
        # Add Farsi header
        markdown.append(f"# {original_data['title']} (فارسی)")
        markdown.append("")
        
        # Add metadata
        markdown.append("## 📋 اطلاعات بخش")
        markdown.append("")
        markdown.append(f"- **عنوان**: {original_data['title']}")
        markdown.append(f"- **صفحه**: {original_data['page']}")
        markdown.append(f"- **منبع**: Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf")
        markdown.append(f"- **تاریخ ترجمه**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown.append("")
        
        # Add original metadata for reference
        markdown.append("## 📄 محتوای اصلی")
        markdown.append("")
        markdown.append(original_data['metadata'])
        markdown.append("")
        
        # Add translated content
        markdown.append("## 📄 محتوای ترجمه شده")
        markdown.append("")
        markdown.append(translated_content)
        
        return '\n'.join(markdown)
    
    def process_single_file(self, file_path: str) -> bool:
        """Process a single markdown file"""
        try:
            print(f"🔄 Processing: {Path(file_path).name}")
            
            # Extract text
            file_data = self.extract_text_from_markdown(file_path)
            if not file_data['content']:
                print(f"⚠️ No content found in {file_path}")
                return False
            
            # Translate content
            print(f"🌐 Translating {len(file_data['content'])} characters...")
            translated_content = self.translate_with_deep_translator(file_data['content'])
            
            # Create Farsi markdown
            farsi_content = self.create_farsi_markdown(file_data, translated_content)
            
            # Save Farsi file
            original_filename = Path(file_path).stem
            farsi_filename = f"{original_filename}_farsi.md"
            farsi_path = os.path.join(self.output_dir, farsi_filename)
            
            with open(farsi_path, 'w', encoding='utf-8') as f:
                f.write(farsi_content)
            
            print(f"✅ Saved: {farsi_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def find_markdown_files(self) -> List[str]:
        """Find all markdown files in input directory"""
        md_files = []
        
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith('.md') and not file.startswith('00_'):
                    md_files.append(os.path.join(root, file))
        
        return sorted(md_files)
    
    def process_all_files(self, max_files: Optional[int] = None) -> Dict:
        """Process all markdown files in input directory"""
        print(f"🔍 Scanning directory: {self.input_dir}")
        
        md_files = self.find_markdown_files()
        
        if not md_files:
            print("❌ No markdown files found!")
            return self.translation_stats
        
        if max_files:
            md_files = md_files[:max_files]
        
        self.translation_stats['total_files'] = len(md_files)
        self.translation_stats['start_time'] = datetime.now()
        
        print(f"📚 Found {len(md_files)} files to process")
        print(f"📁 Output directory: {self.output_dir}")
        print("=" * 50)
        
        for i, file_path in enumerate(md_files, 1):
            print(f"\n[{i}/{len(md_files)}] Processing: {Path(file_path).name}")
            
            success = self.process_single_file(file_path)
            
            if success:
                self.translation_stats['processed'] += 1
            else:
                self.translation_stats['failed'] += 1
            
            # Progress update
            progress = (i / len(md_files)) * 100
            print(f"📊 Progress: {progress:.1f}% ({i}/{len(md_files)})")
            
            # Rate limiting
            time.sleep(1)
        
        self.translation_stats['end_time'] = datetime.now()
        return self.translation_stats
    
    def create_translation_index(self) -> str:
        """Create index of all translated files"""
        index_file = os.path.join(self.output_dir, "00_FARSI_TRANSLATIONS_INDEX.md")
        
        markdown = []
        markdown.append("# 📚 فهرست ترجمه‌های فارسی")
        markdown.append("")
        markdown.append(f"**تاریخ ترجمه**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        markdown.append(f"**منبع**: Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf")
        markdown.append("")
        
        # Find all Farsi files
        farsi_files = []
        for file in os.listdir(self.output_dir):
            if file.endswith('_farsi.md'):
                farsi_files.append(file)
        
        farsi_files.sort()
        
        markdown.append(f"**تعداد فایل‌های ترجمه شده**: {len(farsi_files)}")
        markdown.append("")
        
        # List all files
        markdown.append("## 📄 فایل‌های ترجمه شده")
        markdown.append("")
        
        for file in farsi_files:
            original_name = file.replace('_farsi.md', '.md')
            markdown.append(f"- [{file}]({file}) (اصل: {original_name})")
        
        markdown.append("")
        markdown.append("## 📊 آمار ترجمه")
        markdown.append("")
        markdown.append(f"- **کل فایل‌ها**: {self.translation_stats['total_files']}")
        markdown.append(f"- **ترجمه شده**: {self.translation_stats['processed']}")
        markdown.append(f"- **ناموفق**: {self.translation_stats['failed']}")
        markdown.append(f"- **زمان شروع**: {self.translation_stats['start_time']}")
        markdown.append(f"- **زمان پایان**: {self.translation_stats['end_time']}")
        
        if self.translation_stats['start_time'] and self.translation_stats['end_time']:
            duration = self.translation_stats['end_time'] - self.translation_stats['start_time']
            markdown.append(f"- **مدت زمان**: {duration}")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown))
        
        return index_file
    
    def export_translation_stats(self) -> str:
        """Export translation statistics to JSON"""
        stats_file = os.path.join(self.output_dir, "translation_stats.json")
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.translation_stats, f, indent=2, ensure_ascii=False, default=str)
        
        return stats_file


def main():
    parser = argparse.ArgumentParser(description='Automated Translation Script')
    parser.add_argument('input_dir', help='Input directory containing markdown files')
    parser.add_argument('--output-dir', default='farsi_translations', 
                       help='Output directory for Farsi translations')
    parser.add_argument('--max-files', type=int, 
                       help='Maximum number of files to process (for testing)')
    parser.add_argument('--single-file', 
                       help='Process only a single file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"❌ Input directory '{args.input_dir}' not found")
        return 1
    
    if not DEEP_TRANSLATOR_AVAILABLE:
        print("❌ Deep Translator not available. Please install:")
        print("pip install deep-translator")
        return 1
    
    print("🚀 Automated Translation Script")
    print("=" * 40)
    
    # Create translator
    translator = AutomatedTranslator(args.input_dir, args.output_dir)
    
    try:
        if args.single_file:
            # Process single file
            if not os.path.exists(args.single_file):
                print(f"❌ File '{args.single_file}' not found")
                return 1
            
            print(f"📄 Processing single file: {args.single_file}")
            success = translator.process_single_file(args.single_file)
            
            if success:
                print("✅ Translation completed successfully!")
            else:
                print("❌ Translation failed!")
                return 1
        else:
            # Process all files
            stats = translator.process_all_files(args.max_files)
            
            print("\n" + "=" * 50)
            print("📊 TRANSLATION SUMMARY")
            print("=" * 50)
            print(f"Total files: {stats['total_files']}")
            print(f"Processed: {stats['processed']}")
            print(f"Failed: {stats['failed']}")
            print(f"Success rate: {(stats['processed']/stats['total_files']*100):.1f}%")
            
            if stats['start_time'] and stats['end_time']:
                duration = stats['end_time'] - stats['start_time']
                print(f"Duration: {duration}")
            
            # Create index and stats
            index_file = translator.create_translation_index()
            stats_file = translator.export_translation_stats()
            
            print(f"\n📁 Files saved in: {args.output_dir}")
            print(f"📋 Index created: {index_file}")
            print(f"📊 Stats exported: {stats_file}")
        
        print("\n✅ Translation process completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Translation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
