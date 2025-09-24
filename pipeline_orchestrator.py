#!/usr/bin/env python3
"""
Complete Translation Pipeline Orchestrator
Coordinates chapter extraction, multi-agent translation, and file management
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from pathlib import Path

from chapter_extractor import extract_chapters_from_pages, save_chapters_to_files
from multi_agent_pipeline import MultiAgentTranslationPipeline
from enhanced_database import create_tables, save_pdf_document

class TranslationPipelineOrchestrator:
    def __init__(self, openai_api_key: str = None):
        """Initialize the complete translation pipeline"""
        
        print("🚀 Initializing Complete Translation Pipeline")
        
        # Initialize components
        self.chapter_extractor = None  # Will be initialized when needed
        self.translation_pipeline = MultiAgentTranslationPipeline(openai_api_key)
        
        # Initialize database
        create_tables()
        
        print("✅ Pipeline initialized successfully")
    
    def extract_chapters(self, pages_dir: str = "simple_pages") -> List[Dict[str, Any]]:
        """Extract chapters from page files"""
        
        print(f"📚 Extracting chapters from {pages_dir}/")
        
        chapters = extract_chapters_from_pages(pages_dir)
        
        if not chapters:
            print("❌ No chapters extracted")
            return []
        
        # Save chapters to files
        save_chapters_to_files(chapters)
        
        print(f"✅ Extracted {len(chapters)} chapters")
        return chapters
    
    def translate_chapters(self, chapters: List[Dict[str, Any]], document_id: int = 1) -> List[Dict[str, Any]]:
        """Translate all chapters using multi-agent pipeline"""
        
        print(f"🤖 Starting multi-agent translation for {len(chapters)} chapters")
        
        # Prepare chapter texts
        chapter_texts = []
        for chapter in chapters:
            chapter_texts.append(chapter['content'])
        
        # Process through translation pipeline
        results = self.translation_pipeline.process_document(document_id, chapter_texts)
        
        print(f"✅ Translation completed for {len(results)} chapters")
        return results
    
    def create_final_outputs(self, chapters: List[Dict[str, Any]], translation_results: List[Dict[str, Any]]):
        """Create final output files and summaries"""
        
        print("📄 Creating final outputs...")
        
        # Create output directory
        os.makedirs("final_outputs", exist_ok=True)
        
        # 1. Create complete Farsi document
        farsi_document_path = "final_outputs/complete_farsi_document.txt"
        with open(farsi_document_path, 'w', encoding='utf-8') as f:
            f.write("=== SPEAKING BEING - FARSI TRANSLATION ===\n")
            f.write("ورنر ارهارد، مارتین هایدگر، و امکان جدیدی برای انسان بودن\n")
            f.write("بروس هاید و درو کوپ\n\n")
            f.write("=" * 60 + "\n\n")
            
            for i, chapter in enumerate(chapters):
                f.write(f"=== فصل {i+1}: {chapter['title']} ===\n\n")
                
                # Read translated chapter if exists
                translated_file = f"chapters/chapter_{i+1:03d}_farsi.txt"
                if os.path.exists(translated_file):
                    with open(translated_file, 'r', encoding='utf-8') as tf:
                        f.write(tf.read())
                else:
                    f.write(f"[ترجمه فصل {i+1} در حال انجام است]\n")
                
                f.write("\n" + "=" * 60 + "\n\n")
        
        # 2. Create translation progress report
        progress_report_path = "final_outputs/translation_progress_report.txt"
        with open(progress_report_path, 'w', encoding='utf-8') as f:
            f.write("📊 TRANSLATION PROGRESS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"📚 Total chapters: {len(chapters)}\n")
            f.write(f"🤖 Translation results: {len(translation_results)}\n\n")
            
            f.write("📖 Chapter Status:\n")
            f.write("-" * 30 + "\n")
            
            for i, chapter in enumerate(chapters):
                f.write(f"Chapter {i+1}: {chapter['title']}\n")
                f.write(f"   Pages: {chapter['start_page']}-{chapter['end_page']}\n")
                f.write(f"   Content: {len(chapter['content'])} characters\n")
                
                if i < len(translation_results):
                    result = translation_results[i]
                    f.write(f"   Status: ✅ Translated\n")
                    f.write(f"   Chunks: {result['chunks_processed']}\n")
                    f.write(f"   Terminology: {result['terminology_extracted']} terms\n")
                else:
                    f.write(f"   Status: ⏳ Pending\n")
                
                f.write("\n")
        
        # 3. Create file structure summary
        file_structure_path = "final_outputs/file_structure_summary.txt"
        with open(file_structure_path, 'w', encoding='utf-8') as f:
            f.write("📁 FILE STRUCTURE SUMMARY\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("📂 Project Structure:\n")
            f.write("├── simple_pages/          # Original page files\n")
            f.write("├── chapters/              # Chapter files (EN + FA)\n")
            f.write("├── translated_pages/      # Individual page translations\n")
            f.write("├── final_outputs/        # Final documents\n")
            f.write("└── database/             # PostgreSQL database\n\n")
            
            f.write("📄 Key Files:\n")
            f.write("├── complete_farsi_document.txt    # Complete Farsi book\n")
            f.write("├── translation_progress_report.txt # Progress tracking\n")
            f.write("└── file_structure_summary.txt     # This file\n\n")
            
            f.write("🔧 Scripts:\n")
            f.write("├── extract_all_pages.py           # Extract pages from PDF\n")
            f.write("├── chapter_extractor.py           # Group pages into chapters\n")
            f.write("├── multi_agent_pipeline.py        # AI translation pipeline\n")
            f.write("└── pipeline_orchestrator.py      # This orchestrator\n")
        
        print(f"✅ Final outputs created in final_outputs/")
        print(f"📄 Complete Farsi document: {farsi_document_path}")
        print(f"📊 Progress report: {progress_report_path}")
        print(f"📁 File structure: {file_structure_path}")
    
    def run_complete_pipeline(self, pages_dir: str = "simple_pages", document_id: int = 1):
        """Run the complete translation pipeline"""
        
        print("🚀 Starting Complete Translation Pipeline")
        print("=" * 60)
        
        try:
            # Step 1: Extract chapters
            print("\n📚 STEP 1: Chapter Extraction")
            print("-" * 30)
            chapters = self.extract_chapters(pages_dir)
            
            if not chapters:
                print("❌ No chapters extracted. Pipeline stopped.")
                return
            
            # Step 2: Translate chapters
            print("\n🤖 STEP 2: Multi-Agent Translation")
            print("-" * 30)
            translation_results = self.translate_chapters(chapters, document_id)
            
            # Step 3: Create final outputs
            print("\n📄 STEP 3: Final Output Creation")
            print("-" * 30)
            self.create_final_outputs(chapters, translation_results)
            
            print("\n🎉 Complete Translation Pipeline Finished!")
            print("=" * 60)
            print(f"📊 Results:")
            print(f"   Chapters processed: {len(chapters)}")
            print(f"   Translation results: {len(translation_results)}")
            print(f"   Output directory: final_outputs/")
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            raise

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description="Complete Translation Pipeline")
    parser.add_argument("--pages-dir", default="simple_pages", help="Directory containing page files")
    parser.add_argument("--document-id", type=int, default=1, help="Document ID for database")
    parser.add_argument("--openai-key", help="OpenAI API key")
    parser.add_argument("--extract-only", action="store_true", help="Only extract chapters, don't translate")
    parser.add_argument("--translate-only", action="store_true", help="Only translate existing chapters")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = TranslationPipelineOrchestrator(args.openai_key)
    
    if args.extract_only:
        # Only extract chapters
        chapters = orchestrator.extract_chapters(args.pages_dir)
        print(f"✅ Extracted {len(chapters)} chapters")
        
    elif args.translate_only:
        # Only translate existing chapters
        chapters = extract_chapters_from_pages(args.pages_dir)
        if chapters:
            translation_results = orchestrator.translate_chapters(chapters, args.document_id)
            orchestrator.create_final_outputs(chapters, translation_results)
        else:
            print("❌ No chapters found to translate")
    
    else:
        # Run complete pipeline
        orchestrator.run_complete_pipeline(args.pages_dir, args.document_id)

if __name__ == "__main__":
    main()
