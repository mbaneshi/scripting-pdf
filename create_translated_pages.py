#!/usr/bin/env python3
"""
Create Translated Pages - Create Farsi translations for extracted pages
Usage: python create_translated_pages.py <page_number> <farsi_text>
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def create_translated_page(page_number, farsi_text, source_dir="extracted_pages", output_dir="translated_pages"):
    """Create a translated version of a specific page"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Source file path
    source_filename = f"page_{page_number:03d}.txt"
    source_filepath = os.path.join(source_dir, source_filename)
    
    # Check if source file exists
    if not os.path.exists(source_filepath):
        print(f"❌ Source file not found: {source_filepath}")
        return False
    
    # Translated file path
    translated_filename = f"page_{page_number:03d}_farsi.txt"
    translated_filepath = os.path.join(output_dir, translated_filename)
    
    # Read original text
    try:
        with open(source_filepath, 'r', encoding='utf-8') as f:
            original_text = f.read()
    except Exception as e:
        print(f"❌ Error reading source file: {str(e)}")
        return False
    
    # Create translated file
    try:
        with open(translated_filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== PAGE {page_number} - FARSI TRANSLATION ===\n\n")
            f.write(farsi_text)
            f.write(f"\n\n=== ORIGINAL TEXT ===\n")
            f.write(original_text)
            f.write(f"\n\n=== TRANSLATION INFO ===\n")
            f.write(f"Translated by: AI Assistant\n")
            f.write(f"Translation date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: {source_filename}")
        
        print(f"✅ Translation saved!")
        print(f"📁 File: {translated_filepath}")
        print(f"📊 Text length: {len(farsi_text)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Error creating translated file: {str(e)}")
        return False

def list_available_pages(source_dir="extracted_pages"):
    """List all available pages for translation"""
    
    if not os.path.exists(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        return []
    
    pages = []
    for file in os.listdir(source_dir):
        if file.startswith("page_") and file.endswith(".txt") and "_farsi" not in file:
            try:
                page_num = int(file.split("_")[1].split(".")[0])
                pages.append(page_num)
            except:
                continue
    
    pages.sort()
    return pages

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_translated_pages.py <page_number> <farsi_text> [source_directory]")
        print("Example: python create_translated_pages.py 1 'میلیون‌ها نفر ایده‌های ورنر ارهارد را تجربه کرده‌اند' simple_pages")
        print("\nAvailable pages:")
        pages = list_available_pages()
        if pages:
            print(f"Pages 1-{len(pages)}: {', '.join(map(str, pages[:10]))}{'...' if len(pages) > 10 else ''}")
        else:
            print("No pages found. Run extract_all_pages.py first.")
        sys.exit(1)
    
    try:
        page_number = int(sys.argv[1])
        farsi_text = sys.argv[2]
        source_dir = sys.argv[3] if len(sys.argv) > 3 else "extracted_pages"
        
        success = create_translated_page(page_number, farsi_text, source_dir)
        if success:
            print(f"\n🎉 Farsi translation for page {page_number} created successfully!")
        else:
            sys.exit(1)
            
    except ValueError:
        print("❌ Page number must be an integer")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
