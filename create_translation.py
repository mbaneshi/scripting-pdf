#!/usr/bin/env python3
"""
Simple Translation Helper - Create translation files manually
Usage: python create_translation.py <page_number> <farsi_text>
"""

import sys
import os
from datetime import datetime
from database import create_tables, get_page_by_id, save_translation_job

def create_translation_file(page_number, farsi_text):
    """Create a translation file for a specific page"""
    
    # Initialize database
    create_tables()
    
    # Get page from database
    page = get_page_by_id(page_number)
    if not page:
        print(f"❌ Page {page_number} not found in database")
        return False
    
    # Create output directory
    output_dir = "translated_pages"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create translation file
    filename = f"page_{page_number:03d}_translated.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"=== PAGE {page_number} - TRANSLATED ===\n\n")
        f.write(farsi_text)
        f.write(f"\n\n=== TRANSLATION NOTES ===\n")
        f.write(f"Manual translation provided")
        f.write(f"\n\n=== TRANSLATED BY ===\n")
        f.write("AI Assistant")
        f.write(f"\n=== TRANSLATION DATE ===\n")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Save to database
    try:
        job_id = save_translation_job(
            page_id=page_number,
            original_text=page.original_text,
            translated_text=farsi_text,
            translator="AI Assistant",
            notes="Manual translation provided"
        )
        
        print(f"✅ Translation saved!")
        print(f"📁 File: {filepath}")
        print(f"💾 Database job ID: {job_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python create_translation.py <page_number> <farsi_text>")
        print("Example: python create_translation.py 1 'میلیون‌ها نفر ایده‌های ورنر ارهارد را تجربه کرده‌اند'")
        sys.exit(1)
    
    try:
        page_number = int(sys.argv[1])
        farsi_text = sys.argv[2]
        
        success = create_translation_file(page_number, farsi_text)
        if success:
            print(f"\n🎉 Translation for page {page_number} created successfully!")
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
