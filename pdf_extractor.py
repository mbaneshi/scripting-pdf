#!/usr/bin/env python3
"""
PDF Extractor Script - Extract PDF content page by page and store in database
Usage: python pdf_extractor.py <pdf_file_path> [--pages 50]
"""

import sys
import os
import json
import argparse
from pathlib import Path
import fitz  # PyMuPDF
from datetime import datetime
from database import create_tables, save_pdf_document, save_pdf_page

def extract_page_structure(page, page_number):
    """Extract detailed structure from a single PDF page"""
    
    # Get page dimensions
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    # Extract text with detailed positioning
    text_dict = page.get_text("dict")
    
    # Process text blocks
    text_blocks = []
    fonts_used = set()
    images_info = []
    
    for block in text_dict["blocks"]:
        if "lines" in block:  # Text block
            block_text = ""
            block_info = {
                "bbox": block["bbox"],
                "lines": []
            }
            
            for line in block["lines"]:
                line_text = ""
                line_info = {
                    "bbox": line["bbox"],
                    "spans": []
                }
                
                for span in line["spans"]:
                    span_text = span["text"]
                    line_text += span_text
                    
                    # Track font information
                    font_name = span.get("font", "unknown")
                    font_size = span.get("size", 12)
                    fonts_used.add(f"{font_name}_{font_size}")
                    
                    span_info = {
                        "text": span_text,
                        "font": font_name,
                        "size": font_size,
                        "flags": span.get("flags", 0),
                        "color": span.get("color", 0),
                        "bbox": span["bbox"]
                    }
                    line_info["spans"].append(span_info)
                
                line_info["text"] = line_text
                block_info["lines"].append(line_info)
                block_text += line_text + "\n"
            
            block_info["text"] = block_text.strip()
            text_blocks.append(block_info)
        
        elif "image" in block:  # Image block
            img_info = {
                "bbox": block["bbox"],
                "width": block["width"],
                "height": block["height"],
                "ext": block.get("ext", "unknown")
            }
            images_info.append(img_info)
    
    # Extract plain text
    plain_text = page.get_text()
    
    # Analyze layout
    layout_info = {
        "page_width": page_width,
        "page_height": page_height,
        "text_blocks_count": len(text_blocks),
        "images_count": len(images_info),
        "has_columns": detect_columns(text_blocks),
        "margins": detect_margins(text_blocks, page_width, page_height)
    }
    
    return {
        "plain_text": plain_text,
        "text_blocks": text_blocks,
        "layout_info": layout_info,
        "fonts_used": list(fonts_used),
        "images_info": images_info
    }

def detect_columns(text_blocks):
    """Detect if page has multiple columns"""
    if len(text_blocks) < 2:
        return False
    
    # Simple column detection based on x-coordinates
    x_positions = []
    for block in text_blocks:
        x_positions.append(block["bbox"][0])
    
    # Check if there are distinct x-position clusters
    x_positions.sort()
    clusters = []
    current_cluster = [x_positions[0]]
    
    for i in range(1, len(x_positions)):
        if x_positions[i] - x_positions[i-1] > 50:  # Threshold for column separation
            clusters.append(current_cluster)
            current_cluster = [x_positions[i]]
        else:
            current_cluster.append(x_positions[i])
    
    clusters.append(current_cluster)
    return len(clusters) > 1

def detect_margins(text_blocks, page_width, page_height):
    """Detect page margins based on text block positions"""
    if not text_blocks:
        return {"top": 0, "bottom": 0, "left": 0, "right": 0}
    
    left_margin = min(block["bbox"][0] for block in text_blocks)
    right_margin = page_width - max(block["bbox"][2] for block in text_blocks)
    top_margin = min(block["bbox"][1] for block in text_blocks)
    bottom_margin = page_height - max(block["bbox"][3] for block in text_blocks)
    
    return {
        "top": round(top_margin, 2),
        "bottom": round(bottom_margin, 2),
        "left": round(left_margin, 2),
        "right": round(right_margin, 2)
    }

def save_page_to_file(page_data, page_number, output_dir):
    """Save page text to individual file"""
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"page_{page_number:03d}_original.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"=== PAGE {page_number} ===\n\n")
        f.write(page_data["plain_text"])
        f.write(f"\n\n=== LAYOUT INFO ===\n")
        f.write(json.dumps(page_data["layout_info"], indent=2))
        f.write(f"\n\n=== FONTS USED ===\n")
        f.write("\n".join(page_data["fonts_used"]))
    
    return filepath

def extract_pdf(pdf_path, max_pages=50):
    """Extract PDF content and save to database"""
    
    print(f"📄 Extracting PDF: {pdf_path}")
    print(f"📊 Processing first {max_pages} pages...")
    
    # Create output directory
    output_dir = "extracted_pages"
    os.makedirs(output_dir, exist_ok=True)
    
    # Open PDF
    doc = fitz.open(pdf_path)
    file_size = os.path.getsize(pdf_path)
    page_count = doc.page_count
    
    print(f"📈 PDF Info: {page_count} pages, {file_size/1024:.1f} KB")
    
    # Save document metadata
    document_id = save_pdf_document(
        filename=os.path.basename(pdf_path),
        file_size=file_size,
        page_count=page_count
    )
    
    print(f"💾 Document saved with ID: {document_id}")
    
    # Process pages
    pages_to_process = min(max_pages, page_count)
    processed_pages = 0
    
    for page_num in range(pages_to_process):
        try:
            print(f"🔄 Processing page {page_num + 1}/{pages_to_process}...")
            
            page = doc.load_page(page_num)
            page_data = extract_page_structure(page, page_num + 1)
            
            # Save page text to file
            text_file_path = save_page_to_file(page_data, page_num + 1, output_dir)
            
            # Save to database
            page_id = save_pdf_page(
                document_id=document_id,
                page_number=page_num + 1,
                text=page_data["plain_text"],
                text_blocks=page_data["text_blocks"],
                layout_info=page_data["layout_info"],
                fonts_used=page_data["fonts_used"],
                images_info=page_data["images_info"],
                text_file_path=text_file_path
            )
            
            processed_pages += 1
            print(f"✅ Page {page_num + 1} saved (ID: {page_id})")
            
        except Exception as e:
            print(f"❌ Error processing page {page_num + 1}: {str(e)}")
            continue
    
    doc.close()
    
    print(f"\n🎉 Extraction completed!")
    print(f"📊 Processed: {processed_pages}/{pages_to_process} pages")
    print(f"📁 Text files saved in: {output_dir}/")
    print(f"💾 Database entries created")
    
    return document_id, processed_pages

def main():
    parser = argparse.ArgumentParser(description="Extract PDF content page by page")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--pages", type=int, default=50, help="Number of pages to process (default: 50)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Initialize database
    create_tables()
    
    # Extract PDF
    try:
        document_id, processed_pages = extract_pdf(args.pdf_path, args.pages)
        print(f"\n🚀 Ready for translation! Document ID: {document_id}")
        print(f"📝 Run: python translation_manager.py --document {document_id}")
        
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()