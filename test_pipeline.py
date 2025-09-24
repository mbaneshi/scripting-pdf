#!/usr/bin/env python3
"""
Complete PDF Translation Pipeline - Test Script
Usage: python test_pipeline.py
"""

import os
import sys
from pathlib import Path

def test_pipeline():
    """Test the complete PDF translation pipeline"""
    
    print("🚀 PDF Translation Pipeline Test")
    print("=" * 50)
    
    # Check if PDF exists
    pdf_file = "Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf"
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return False
    
    print(f"✅ PDF file found: {pdf_file}")
    
    # Step 1: Extract PDF
    print(f"\n📄 Step 1: Extract PDF content")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run([
            "uv", "run", "python", "pdf_extractor.py", pdf_file, "--pages", "5"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PDF extraction completed")
            print("📁 Check 'extracted_pages/' directory for text files")
        else:
            print(f"❌ PDF extraction failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running PDF extractor: {str(e)}")
        return False
    
    # Step 2: Check database
    print(f"\n💾 Step 2: Check database")
    print("-" * 30)
    
    try:
        from database import create_tables, get_documents, get_pages_ready_for_translation
        
        create_tables()
        documents = get_documents()
        
        if documents:
            doc = documents[0]
            print(f"✅ Document found: {doc.filename}")
            print(f"📊 Pages: {doc.page_count}")
            
            pages = get_pages_ready_for_translation(doc.id, limit=5)
            print(f"🔄 Pages ready for translation: {len(pages)}")
            
            if pages:
                print("📋 Sample pages:")
                for page in pages[:3]:
                    print(f"  - Page {page.page_number} (ID: {page.id})")
        else:
            print("❌ No documents found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False
    
    # Step 3: Test translation manager
    print(f"\n🤖 Step 3: Test translation manager")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            "uv", "run", "python", "translation_manager.py", "--document", str(doc.id), "--status"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Translation manager working")
            print("📋 Status check completed")
        else:
            print(f"❌ Translation manager failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running translation manager: {str(e)}")
        return False
    
    # Step 4: Test PDF reconstructor
    print(f"\n📄 Step 4: Test PDF reconstructor")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            "uv", "run", "python", "pdf_reconstructor.py", "--document", str(doc.id), "--output", "test_output.pdf"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PDF reconstructor working")
            print("📁 Check 'output/' directory for generated PDF")
        else:
            print(f"❌ PDF reconstructor failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running PDF reconstructor: {str(e)}")
        return False
    
    print(f"\n🎉 Pipeline test completed successfully!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Run: python pdf_extractor.py <pdf_file> --pages 50")
    print("2. Run: python translation_manager.py --document <doc_id>")
    print("3. Provide translations for each page")
    print("4. Run: python pdf_reconstructor.py --document <doc_id>")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_pipeline()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
