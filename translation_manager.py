#!/usr/bin/env python3
"""
Translation Manager Script - Manage manual translation workflow
Usage: python translation_manager.py --document <doc_id> [--pages 50]
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from database import (
    create_tables, get_document_by_id, get_pages_ready_for_translation,
    get_page_by_id, save_translation_job
)

def show_translation_status(document_id):
    """Show current translation status"""
    document = get_document_by_id(document_id)
    if not document:
        print(f"❌ Document {document_id} not found")
        return
    
    pages = get_pages_ready_for_translation(document_id)
    
    print(f"📄 Document: {document.filename}")
    print(f"📊 Total pages: {document.page_count}")
    print(f"🔄 Pages ready for translation: {len(pages)}")
    
    if pages:
        print(f"\n📋 Pages ready for translation:")
        for page in pages[:10]:  # Show first 10
            print(f"  - Page {page.page_number} (ID: {page.id})")
        if len(pages) > 10:
            print(f"  ... and {len(pages) - 10} more pages")

def get_next_page_for_translation(document_id):
    """Get next page that needs translation"""
    pages = get_pages_ready_for_translation(document_id, limit=1)
    return pages[0] if pages else None

def show_page_content(page_id):
    """Show page content for translation"""
    page = get_page_by_id(page_id)
    if not page:
        print(f"❌ Page {page_id} not found")
        return None
    
    print(f"\n📄 PAGE {page.page_number} - Translation Ready")
    print("=" * 60)
    
    # Show original text
    print("📝 ORIGINAL TEXT:")
    print("-" * 40)
    print(page.original_text)
    
    # Show layout info
    if page.layout_info:
        layout = json.loads(page.layout_info) if isinstance(page.layout_info, str) else page.layout_info
        print(f"\n📐 LAYOUT INFO:")
        print(f"  - Page size: {layout.get('page_width', 'N/A')} x {layout.get('page_height', 'N/A')}")
        print(f"  - Text blocks: {layout.get('text_blocks_count', 'N/A')}")
        print(f"  - Has columns: {layout.get('has_columns', 'N/A')}")
        print(f"  - Images: {layout.get('images_count', 'N/A')}")
    
    # Show fonts used
    if page.fonts_used:
        fonts = json.loads(page.fonts_used) if isinstance(page.fonts_used, str) else page.fonts_used
        print(f"\n🔤 FONTS USED:")
        for font in fonts[:5]:  # Show first 5 fonts
            print(f"  - {font}")
        if len(fonts) > 5:
            print(f"  ... and {len(fonts) - 5} more fonts")
    
    print("\n" + "=" * 60)
    return page

def save_translation(page_id, translated_text, notes=""):
    """Save translation to database and file"""
    page = get_page_by_id(page_id)
    if not page:
        print(f"❌ Page {page_id} not found")
        return False
    
    try:
        # Save to database
        job_id = save_translation_job(
            page_id=page_id,
            original_text=page.original_text,
            translated_text=translated_text,
            translator="AI Assistant",
            notes=notes
        )
        
        # Save to file
        output_dir = "translated_pages"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"page_{page.page_number:03d}_translated.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== PAGE {page.page_number} - TRANSLATED ===\n\n")
            f.write(translated_text)
            f.write(f"\n\n=== TRANSLATION NOTES ===\n")
            f.write(notes)
            f.write(f"\n\n=== TRANSLATED BY ===\n")
            f.write("AI Assistant")
            f.write(f"\n=== TRANSLATION DATE ===\n")
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        print(f"✅ Translation saved!")
        print(f"📁 File: {filepath}")
        print(f"💾 Database job ID: {job_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving translation: {str(e)}")
        return False

def interactive_translation_mode(document_id, max_pages=50):
    """Interactive translation mode"""
    print(f"🚀 Starting interactive translation mode")
    print(f"📄 Document ID: {document_id}")
    print(f"📊 Max pages: {max_pages}")
    
    pages_processed = 0
    
    while pages_processed < max_pages:
        # Get next page
        page = get_next_page_for_translation(document_id)
        if not page:
            print(f"\n🎉 All pages translated!")
            break
        
        # Show page content
        page_data = show_page_content(page.id)
        if not page_data:
            break
        
        print(f"\n🤖 AI Translation:")
        print("=" * 60)
        
        # Here you would provide the translation
        # For now, we'll create a placeholder
        print("Please provide the Farsi translation for this page...")
        print("(This is where you would input the translation)")
        
        # Placeholder translation (you would replace this)
        translated_text = f"[FARSI TRANSLATION FOR PAGE {page.page_number}]\n\n{page_data.original_text}"
        notes = f"Translated page {page.page_number} - placeholder translation"
        
        # Save translation
        if save_translation(page.id, translated_text, notes):
            pages_processed += 1
            print(f"\n📊 Progress: {pages_processed}/{max_pages} pages completed")
        
        # Ask if user wants to continue
        if pages_processed < max_pages:
            continue_translation = input(f"\nContinue with next page? (y/n): ").lower().strip()
            if continue_translation != 'y':
                break
    
    print(f"\n🎉 Translation session completed!")
    print(f"📊 Pages processed: {pages_processed}")

def batch_translation_mode(document_id, max_pages=50):
    """Batch translation mode - show all pages ready for translation"""
    pages = get_pages_ready_for_translation(document_id, limit=max_pages)
    
    if not pages:
        print(f"❌ No pages ready for translation")
        return
    
    print(f"📋 BATCH TRANSLATION MODE")
    print(f"📄 Document ID: {document_id}")
    print(f"📊 Pages ready: {len(pages)}")
    
    for i, page in enumerate(pages, 1):
        print(f"\n{'='*60}")
        print(f"PAGE {page.page_number} ({i}/{len(pages)})")
        print(f"{'='*60}")
        
        # Show page content
        show_page_content(page.id)
        
        print(f"\n🤖 TRANSLATION REQUIRED:")
        print("Please provide Farsi translation for this page...")
        
        # Here you would provide the actual translation
        translated_text = f"[FARSI TRANSLATION FOR PAGE {page.page_number}]\n\n{page.original_text}"
        notes = f"Batch translation - page {page.page_number}"
        
        # Save translation
        save_translation(page.id, translated_text, notes)
        
        if i < len(pages):
            input(f"\nPress Enter to continue to next page...")

def main():
    parser = argparse.ArgumentParser(description="Manage PDF translation workflow")
    parser.add_argument("--document", type=int, required=True, help="Document ID")
    parser.add_argument("--pages", type=int, default=50, help="Number of pages to process")
    parser.add_argument("--mode", choices=["interactive", "batch"], default="interactive", 
                       help="Translation mode")
    parser.add_argument("--status", action="store_true", help="Show translation status only")
    
    args = parser.parse_args()
    
    # Initialize database
    create_tables()
    
    if args.status:
        show_translation_status(args.document)
        return
    
    if args.mode == "interactive":
        interactive_translation_mode(args.document, args.pages)
    elif args.mode == "batch":
        batch_translation_mode(args.document, args.pages)

if __name__ == "__main__":
    main()
