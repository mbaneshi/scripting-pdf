#!/usr/bin/env python3
"""
Simple PDF Text Extractor - Extract all pages to individual text files
Usage: python extract_all_pages.py <pdf_file> [output_directory]
"""

import sys
import os
import argparse
import fitz  # PyMuPDF
from pathlib import Path

def extract_all_pages(pdf_path, output_dir="extracted_pages"):
    """Extract all pages from PDF to individual text files"""
    
    print(f"📄 Extracting PDF: {pdf_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Open PDF
    try:
        doc = fitz.open(pdf_path)
        page_count = doc.page_count
        file_size = os.path.getsize(pdf_path)
        
        print(f"📊 PDF Info: {page_count} pages, {file_size/1024:.1f} KB")
        print(f"📁 Output directory: {output_dir}/")
        
    except Exception as e:
        print(f"❌ Error opening PDF: {str(e)}")
        return False
    
    # Process each page
    extracted_count = 0
    
    for page_num in range(page_count):
        try:
            print(f"🔄 Processing page {page_num + 1}/{page_count}...")
            
            # Load page
            page = doc.load_page(page_num)
            
            # Extract text
            text = page.get_text()
            
            # Create filename
            filename = f"page_{page_num + 1:03d}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Write text to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== PAGE {page_num + 1} ===\n\n")
                f.write(text)
                f.write(f"\n\n=== END OF PAGE {page_num + 1} ===")
            
            extracted_count += 1
            
            # Show progress every 10 pages
            if (page_num + 1) % 10 == 0:
                print(f"✅ Processed {page_num + 1} pages...")
                
        except Exception as e:
            print(f"❌ Error processing page {page_num + 1}: {str(e)}")
            continue
    
    # Close document
    doc.close()
    
    print(f"\n🎉 Extraction completed!")
    print(f"📊 Successfully extracted: {extracted_count}/{page_count} pages")
    print(f"📁 Text files saved in: {output_dir}/")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Extract all PDF pages to individual text files")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("output_dir", nargs="?", default="extracted_pages", 
                       help="Output directory (default: extracted_pages)")
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Extract pages
    try:
        success = extract_all_pages(args.pdf_path, args.output_dir)
        if success:
            print(f"\n🚀 Ready for translation!")
            print(f"📝 Each page is now in a separate text file")
            print(f"📁 Directory: {args.output_dir}/")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Extraction failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
