#!/usr/bin/env python3
"""
Batch Translation Script - Translate multiple pages systematically
Usage: python batch_translate.py <start_page> <end_page> [source_directory]
"""

import sys
import os
from pathlib import Path

def translate_page_batch(start_page, end_page, source_dir="simple_pages"):
    """Translate a batch of pages from start_page to end_page"""
    
    print(f"🔄 Batch Translation: Pages {start_page} to {end_page}")
    print(f"📁 Source directory: {source_dir}")
    print("=" * 60)
    
    translated_count = 0
    skipped_count = 0
    
    for page_num in range(start_page, end_page + 1):
        print(f"\n📄 PAGE {page_num}")
        print("-" * 40)
        
        # Check if source file exists
        source_file = os.path.join(source_dir, f"page_{page_num:03d}.txt")
        if not os.path.exists(source_file):
            print(f"❌ Source file not found: {source_file}")
            skipped_count += 1
            continue
        
        # Check if already translated
        translated_file = f"translated_pages/page_{page_num:03d}_farsi.txt"
        if os.path.exists(translated_file):
            print(f"✅ Already translated: {translated_file}")
            translated_count += 1
            continue
        
        # Read original text
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                original_text = f.read()
        except Exception as e:
            print(f"❌ Error reading source file: {str(e)}")
            skipped_count += 1
            continue
        
        # Show original text preview
        lines = original_text.split('\n')
        preview_lines = [line for line in lines if line.strip() and not line.startswith('===')][:5]
        print("📝 Original text preview:")
        for line in preview_lines:
            print(f"   {line[:80]}{'...' if len(line) > 80 else ''}")
        
        print(f"\n🤖 Please provide Farsi translation for page {page_num}:")
        print("(Type your translation, then press Enter twice to finish)")
        print("-" * 40)
        
        # Get translation from user
        translated_lines = []
        try:
            while True:
                line = input()
                if line.strip() == "" and len(translated_lines) > 0:
                    break
                translated_lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print(f"\n⏹️  Skipping page {page_num}")
            skipped_count += 1
            continue
        
        farsi_text = "\n".join(translated_lines).strip()
        
        if not farsi_text:
            print(f"⚠️  No translation provided, skipping page {page_num}")
            skipped_count += 1
            continue
        
        # Create translated file
        try:
            os.makedirs("translated_pages", exist_ok=True)
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(f"=== PAGE {page_num} - FARSI TRANSLATION ===\n\n")
                f.write(farsi_text)
                f.write(f"\n\n=== ORIGINAL TEXT ===\n")
                f.write(original_text)
                f.write(f"\n\n=== TRANSLATION INFO ===\n")
                f.write(f"Translated by: AI Assistant\n")
                f.write(f"Translation date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source file: page_{page_num:03d}.txt")
            
            print(f"✅ Translation saved: {translated_file}")
            translated_count += 1
            
        except Exception as e:
            print(f"❌ Error saving translation: {str(e)}")
            skipped_count += 1
            continue
        
        # Show progress
        total_processed = translated_count + skipped_count
        print(f"\n📊 Progress: {total_processed}/{end_page - start_page + 1} pages processed")
        print(f"✅ Translated: {translated_count}")
        print(f"⏭️  Skipped: {skipped_count}")
    
    print(f"\n🎉 Batch translation completed!")
    print(f"📊 Final results:")
    print(f"✅ Translated: {translated_count} pages")
    print(f"⏭️  Skipped: {skipped_count} pages")
    print(f"📁 Translations saved in: translated_pages/")

def main():
    if len(sys.argv) < 3:
        print("Usage: python batch_translate.py <start_page> <end_page> [source_directory]")
        print("Example: python batch_translate.py 1 10 simple_pages")
        print("Example: python batch_translate.py 1 50 simple_pages")
        print("Example: python batch_translate.py 1 579 simple_pages  # All pages")
        sys.exit(1)
    
    try:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
        source_dir = sys.argv[3] if len(sys.argv) > 3 else "simple_pages"
        
        if start_page > end_page:
            print("❌ Start page must be less than or equal to end page")
            sys.exit(1)
        
        if not os.path.exists(source_dir):
            print(f"❌ Source directory not found: {source_dir}")
            sys.exit(1)
        
        translate_page_batch(start_page, end_page, source_dir)
        
    except ValueError:
        print("❌ Page numbers must be integers")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
