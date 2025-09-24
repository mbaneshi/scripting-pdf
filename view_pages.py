#!/usr/bin/env python3
"""
Page Content Viewer - View content of pages to decide what to translate
Usage: python view_pages.py <start_page> <end_page> [source_directory]
"""

import sys
import os

def view_pages(start_page, end_page, source_dir="simple_pages"):
    """View content of pages from start_page to end_page"""
    
    print(f"📄 Viewing Pages: {start_page} to {end_page}")
    print(f"📁 Source directory: {source_dir}")
    print("=" * 60)
    
    for page_num in range(start_page, end_page + 1):
        source_file = os.path.join(source_dir, f"page_{page_num:03d}.txt")
        
        if not os.path.exists(source_file):
            print(f"\n❌ Page {page_num}: File not found")
            continue
        
        print(f"\n📄 PAGE {page_num}")
        print("-" * 40)
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean content (remove headers)
            lines = content.split('\n')
            content_lines = [line for line in lines if line.strip() and not line.startswith('===')]
            
            if content_lines:
                print("📝 Content:")
                for i, line in enumerate(content_lines[:10]):  # Show first 10 lines
                    print(f"   {line}")
                if len(content_lines) > 10:
                    print(f"   ... ({len(content_lines) - 10} more lines)")
                
                print(f"\n📊 Stats:")
                print(f"   - Total lines: {len(content_lines)}")
                print(f"   - Characters: {len(content)}")
                print(f"   - File size: {os.path.getsize(source_file)} bytes")
            else:
                print("📝 Content: (Empty or whitespace only)")
                
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
        
        # Check if already translated
        translated_file = f"translated_pages/page_{page_num:03d}_farsi.txt"
        if os.path.exists(translated_file):
            print(f"✅ Already translated: {translated_file}")
        else:
            print(f"⏳ Not translated yet")
        
        print("-" * 40)

def main():
    if len(sys.argv) < 3:
        print("Usage: python view_pages.py <start_page> <end_page> [source_directory]")
        print("Example: python view_pages.py 1 10 simple_pages")
        print("Example: python view_pages.py 1 50 simple_pages")
        print("Example: python view_pages.py 100 120 simple_pages")
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
        
        view_pages(start_page, end_page, source_dir)
        
    except ValueError:
        print("❌ Page numbers must be integers")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
