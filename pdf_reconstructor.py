#!/usr/bin/env python3
"""
PDF Reconstructor Script - Rebuild PDF with Farsi translations
Usage: python pdf_reconstructor.py --document <doc_id> [--output farsi_output.pdf]
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from database import (
    create_tables, get_document_by_id, get_pages_by_document,
    get_page_by_id
)

def register_farsi_fonts():
    """Register Farsi fonts (Vazirmatn) for PDF generation"""
    try:
        # Try to register Vazirmatn fonts
        # You would need to download Vazirmatn fonts and place them in fonts/ directory
        
        font_dir = "fonts"
        if os.path.exists(font_dir):
            # Register Vazirmatn fonts
            vazirmatn_regular = os.path.join(font_dir, "Vazirmatn-Regular.ttf")
            vazirmatn_bold = os.path.join(font_dir, "Vazirmatn-Bold.ttf")
            
            if os.path.exists(vazirmatn_regular):
                pdfmetrics.registerFont(TTFont('Vazirmatn-Regular', vazirmatn_regular))
                print("✅ Vazirmatn-Regular font registered")
            
            if os.path.exists(vazirmatn_bold):
                pdfmetrics.registerFont(TTFont('Vazirmatn-Bold', vazirmatn_bold))
                print("✅ Vazirmatn-Bold font registered")
            
            # Font mapping
            addMapping('Vazirmatn-Regular', 0, 0, 'Vazirmatn-Regular')
            addMapping('Vazirmatn-Bold', 0, 1, 'Vazirmatn-Bold')
            
            return True
        else:
            print("⚠️  Fonts directory not found, using default fonts")
            return False
            
    except Exception as e:
        print(f"⚠️  Font registration failed: {str(e)}")
        print("Using default fonts")
        return False

def create_farsi_styles():
    """Create Farsi-specific paragraph styles"""
    styles = getSampleStyleSheet()
    
    # Register fonts first
    fonts_available = register_farsi_fonts()
    
    if fonts_available:
        # Farsi styles with Vazirmatn
        farsi_normal = ParagraphStyle(
            'FarsiNormal',
            parent=styles['Normal'],
            fontName='Vazirmatn-Regular',
            fontSize=12,
            leading=16,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=6
        )
        
        farsi_bold = ParagraphStyle(
            'FarsiBold',
            parent=styles['Normal'],
            fontName='Vazirmatn-Bold',
            fontSize=12,
            leading=16,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=6
        )
        
        farsi_title = ParagraphStyle(
            'FarsiTitle',
            parent=styles['Title'],
            fontName='Vazirmatn-Bold',
            fontSize=16,
            leading=20,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=12
        )
    else:
        # Fallback styles with default fonts
        farsi_normal = ParagraphStyle(
            'FarsiNormal',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=6
        )
        
        farsi_bold = ParagraphStyle(
            'FarsiBold',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=6
        )
        
        farsi_title = ParagraphStyle(
            'FarsiTitle',
            parent=styles['Title'],
            fontSize=16,
            leading=20,
            alignment=2,  # Right alignment for Farsi
            spaceAfter=12
        )
    
    return {
        'normal': farsi_normal,
        'bold': farsi_bold,
        'title': farsi_title
    }

def get_translated_text(page_id):
    """Get translated text for a page"""
    # This would typically come from the database
    # For now, we'll read from the translated file
    
    page = get_page_by_id(page_id)
    if not page:
        return None
    
    if page.translated_text_file and os.path.exists(page.translated_text_file):
        with open(page.translated_text_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract just the translated text (skip headers)
            lines = content.split('\n')
            translated_lines = []
            in_translation = False
            
            for line in lines:
                if line.startswith('=== PAGE') and 'TRANSLATED ===' in line:
                    in_translation = True
                    continue
                elif line.startswith('=== TRANSLATION NOTES ==='):
                    break
                elif in_translation and line.strip():
                    translated_lines.append(line)
            
            return '\n'.join(translated_lines)
    
    return None

def process_page_layout(page_data, translated_text):
    """Process page layout and create formatted content"""
    if not translated_text:
        return []
    
    styles = create_farsi_styles()
    content = []
    
    # Add page number
    content.append(Paragraph(f"صفحه {page_data.page_number}", styles['title']))
    content.append(Spacer(1, 12))
    
    # Process translated text
    paragraphs = translated_text.split('\n\n')
    
    for para in paragraphs:
        if para.strip():
            # Determine style based on content
            if para.strip().startswith('SPEAKING BEING') or 'SPEAKING BEING' in para:
                content.append(Paragraph(para.strip(), styles['title']))
            elif para.strip().startswith('ERHARD:') or para.strip().startswith('MARSHA:'):
                content.append(Paragraph(para.strip(), styles['bold']))
            else:
                content.append(Paragraph(para.strip(), styles['normal']))
            
            content.append(Spacer(1, 6))
    
    return content

def reconstruct_pdf(document_id, output_path):
    """Reconstruct PDF with Farsi translations"""
    
    print(f"🔄 Reconstructing PDF for document {document_id}")
    
    # Get document info
    document = get_document_by_id(document_id)
    if not document:
        print(f"❌ Document {document_id} not found")
        return False
    
    # Get all pages
    pages = get_pages_by_document(document_id)
    if not pages:
        print(f"❌ No pages found for document {document_id}")
        return False
    
    print(f"📄 Document: {document.filename}")
    print(f"📊 Pages to process: {len(pages)}")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Build content
    story = []
    
    for i, page in enumerate(pages):
        print(f"🔄 Processing page {page.page_number} ({i+1}/{len(pages)})")
        
        # Get translated text
        translated_text = get_translated_text(page.id)
        
        if translated_text:
            # Process page content
            page_content = process_page_layout(page, translated_text)
            story.extend(page_content)
            
            # Add page break (except for last page)
            if i < len(pages) - 1:
                story.append(PageBreak())
        else:
            print(f"⚠️  No translation found for page {page.page_number}")
            # Add placeholder
            story.append(Paragraph(f"صفحه {page.page_number} - ترجمه موجود نیست", create_farsi_styles()['normal']))
            if i < len(pages) - 1:
                story.append(PageBreak())
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF reconstructed successfully!")
        print(f"📁 Output file: {output_path}")
        print(f"📊 Pages processed: {len(pages)}")
        return True
        
    except Exception as e:
        print(f"❌ PDF reconstruction failed: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Reconstruct PDF with Farsi translations")
    parser.add_argument("--document", type=int, required=True, help="Document ID")
    parser.add_argument("--output", default="farsi_output.pdf", help="Output PDF filename")
    
    args = parser.parse_args()
    
    # Initialize database
    create_tables()
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, args.output)
    
    # Reconstruct PDF
    success = reconstruct_pdf(args.document, output_path)
    
    if success:
        print(f"\n🎉 PDF reconstruction completed!")
        print(f"📁 File saved: {output_path}")
        print(f"📊 File size: {os.path.getsize(output_path)/1024:.1f} KB")
    else:
        print(f"\n❌ PDF reconstruction failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
