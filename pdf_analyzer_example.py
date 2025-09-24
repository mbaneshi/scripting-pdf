#!/usr/bin/env python3
"""
Example usage of PDF Text Analyzer
Demonstrates various analysis capabilities
"""

import os
import sys
from pdf_text_analyzer import PDFTextAnalyzer

def analyze_pdf_example(pdf_path: str):
    """Example analysis of a PDF file"""
    
    print(f"Analyzing PDF: {pdf_path}")
    print("=" * 50)
    
    # Create analyzer
    analyzer = PDFTextAnalyzer(pdf_path)
    
    # Load PDF
    if not analyzer.load_pdf():
        print("Failed to load PDF")
        return
    
    try:
        # Extract text
        print("Extracting text...")
        analyzer.extract_text_by_page()
        
        # Basic statistics
        print("\n📊 BASIC STATISTICS:")
        stats = analyzer.get_page_statistics()
        total_words = sum(page['word_count'] for page in stats.values())
        total_chars = sum(page['character_count'] for page in stats.values())
        total_sentences = sum(page['sentence_count'] for page in stats.values())
        
        print(f"  Pages: {len(analyzer.doc)}")
        print(f"  Total words: {total_words:,}")
        print(f"  Total characters: {total_chars:,}")
        print(f"  Total sentences: {total_sentences:,}")
        print(f"  Avg words/page: {total_words / len(analyzer.doc):.1f}")
        
        # Word frequency analysis
        print("\n🔤 WORD FREQUENCY ANALYSIS:")
        word_freq = analyzer.get_word_frequency()
        print(f"  Unique words: {len(word_freq):,}")
        print("  Top 10 words:")
        for i, (word, count) in enumerate(word_freq.most_common(10), 1):
            print(f"    {i:2d}. {word:<15} : {count:>6,}")
        
        # Character frequency
        print("\n📝 CHARACTER FREQUENCY:")
        char_freq = analyzer.get_character_frequency()
        print("  Top 10 characters:")
        for i, (char, count) in enumerate(char_freq.most_common(10), 1):
            char_display = repr(char) if char in '\n\t\r' else char
            print(f"    {i:2d}. {char_display:<8} : {count:>8,}")
        
        # Common phrases
        print("\n📖 COMMON PHRASES (2-word):")
        phrases = analyzer.find_phrases(phrase_length=2, min_frequency=3)
        print(f"  Found {len(phrases)} phrases (freq >= 3)")
        print("  Top 10 phrases:")
        for i, (phrase, count) in enumerate(phrases.most_common(10), 1):
            print(f"    {i:2d}. '{phrase}' : {count}")
        
        # Page-by-page analysis
        print("\n📄 PAGE-BY-PAGE ANALYSIS:")
        print("  Page | Words | Chars | Sentences | Avg W/S")
        print("  -----|-------|-------|-----------|--------")
        for page_num in sorted(stats.keys())[:10]:  # Show first 10 pages
            page_stats = stats[page_num]
            print(f"  {page_num:4d} | {page_stats['word_count']:5d} | "
                  f"{page_stats['character_count']:5d} | "
                  f"{page_stats['sentence_count']:9d} | "
                  f"{page_stats['avg_words_per_sentence']:6.1f}")
        
        if len(stats) > 10:
            print(f"  ... and {len(stats) - 10} more pages")
        
        # Export analysis
        print("\n💾 EXPORTING ANALYSIS...")
        analysis_file = analyzer.export_analysis()
        print(f"  Analysis saved to: {analysis_file}")
        
        # Generate visualizations
        print("\n🎨 GENERATING VISUALIZATIONS...")
        try:
            wordcloud_file = analyzer.generate_word_cloud()
            print(f"  Word cloud saved to: {wordcloud_file}")
        except Exception as e:
            print(f"  Word cloud generation failed: {e}")
        
        try:
            chart_file = analyzer.create_frequency_chart()
            print(f"  Frequency chart saved to: {chart_file}")
        except Exception as e:
            print(f"  Frequency chart generation failed: {e}")
        
        print("\n✅ Analysis complete!")
        
    finally:
        analyzer.close()


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python pdf_analyzer_example.py <pdf_file_path>")
        print("\nAvailable PDF files in current directory:")
        
        # Find PDF files
        pdf_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if pdf_files:
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf_file}")
        else:
            print("  No PDF files found")
        
        return 1
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found")
        return 1
    
    analyze_pdf_example(pdf_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

