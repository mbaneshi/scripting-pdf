#!/usr/bin/env python3
"""
PDF Text Extraction and Analysis Tool
Extracts text from PDF files and performs various data analysis operations
"""

import os
import sys
import re
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import argparse
from pathlib import Path

import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud


class PDFTextAnalyzer:
    """Comprehensive PDF text extraction and analysis tool"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.text_data = {}
        self.metadata = {}
        
    def load_pdf(self) -> bool:
        """Load PDF document"""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.metadata = self.doc.metadata
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def extract_text_by_page(self) -> Dict[int, str]:
        """Extract text from each page"""
        if not self.doc:
            raise ValueError("PDF not loaded. Call load_pdf() first.")
        
        text_data = {}
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            text_data[page_num + 1] = text  # 1-indexed pages
        
        self.text_data = text_data
        return text_data
    
    def extract_all_text(self) -> str:
        """Extract all text as a single string"""
        if not self.text_data:
            self.extract_text_by_page()
        
        return "\n".join(self.text_data.values())
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def get_word_frequency(self, text: str = None, 
                          min_length: int = 3, 
                          case_sensitive: bool = False) -> Counter:
        """Calculate word frequency"""
        if text is None:
            text = self.extract_all_text()
        
        text = self.clean_text(text)
        
        if not case_sensitive:
            text = text.lower()
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', text)
        words = [word for word in words if len(word) >= min_length]
        
        return Counter(words)
    
    def get_character_frequency(self, text: str = None) -> Counter:
        """Calculate character frequency"""
        if text is None:
            text = self.extract_all_text()
        
        return Counter(text)
    
    def get_sentence_count(self, text: str = None) -> int:
        """Count sentences"""
        if text is None:
            text = self.extract_all_text()
        
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def get_paragraph_count(self, text: str = None) -> int:
        """Count paragraphs"""
        if text is None:
            text = self.extract_all_text()
        
        paragraphs = text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    def get_page_statistics(self) -> Dict[int, Dict[str, any]]:
        """Get statistics for each page"""
        if not self.text_data:
            self.extract_text_by_page()
        
        stats = {}
        for page_num, text in self.text_data.items():
            cleaned_text = self.clean_text(text)
            word_count = len(re.findall(r'\b\w+\b', cleaned_text))
            char_count = len(cleaned_text)
            sentence_count = len(re.split(r'[.!?]+', cleaned_text))
            
            stats[page_num] = {
                'word_count': word_count,
                'character_count': char_count,
                'sentence_count': sentence_count,
                'avg_words_per_sentence': word_count / max(sentence_count, 1)
            }
        
        return stats
    
    def find_phrases(self, phrase_length: int = 2, min_frequency: int = 2) -> Counter:
        """Find common phrases (n-grams)"""
        text = self.extract_all_text()
        text = self.clean_text(text).lower()
        
        words = re.findall(r'\b\w+\b', text)
        phrases = []
        
        for i in range(len(words) - phrase_length + 1):
            phrase = ' '.join(words[i:i + phrase_length])
            phrases.append(phrase)
        
        phrase_counter = Counter(phrases)
        return Counter({phrase: count for phrase, count in phrase_counter.items() 
                       if count >= min_frequency})
    
    def search_patterns(self, pattern: str, case_sensitive: bool = False) -> List[Dict]:
        """Search for specific patterns in text"""
        text = self.extract_all_text()
        
        if not case_sensitive:
            pattern = pattern.lower()
            text = text.lower()
        
        matches = []
        for match in re.finditer(pattern, text):
            # Find which page this match is on
            page_num = self._find_page_for_position(match.start())
            matches.append({
                'page': page_num,
                'position': match.start(),
                'text': match.group(),
                'context': self._get_context(text, match.start(), match.end())
            })
        
        return matches
    
    def _find_page_for_position(self, position: int) -> int:
        """Find which page a character position belongs to"""
        if not self.text_data:
            self.extract_text_by_page()
        
        current_pos = 0
        for page_num, text in sorted(self.text_data.items()):
            page_length = len(text) + 1  # +1 for newline
            if position < current_pos + page_length:
                return page_num
            current_pos += page_length
        return len(self.text_data)
    
    def _get_context(self, text: str, start: int, end: int, context_length: int = 50) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        return text[context_start:context_end]
    
    def generate_word_cloud(self, output_path: str = None, 
                           max_words: int = 100) -> str:
        """Generate word cloud"""
        text = self.extract_all_text()
        word_freq = self.get_word_frequency(text)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
        
        filtered_words = {word: count for word, count in word_freq.items() 
                        if word.lower() not in stop_words}
        
        if not filtered_words:
            return "No words to generate word cloud"
        
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white',
                            max_words=max_words).generate_from_frequencies(filtered_words)
        
        if output_path is None:
            output_path = f"{Path(self.pdf_path).stem}_wordcloud.png"
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud - {Path(self.pdf_path).name}')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_frequency_chart(self, output_path: str = None, 
                             top_n: int = 20) -> str:
        """Create frequency chart for top words"""
        word_freq = self.get_word_frequency()
        top_words = word_freq.most_common(top_n)
        
        if not top_words:
            return "No words to chart"
        
        words, counts = zip(*top_words)
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(range(len(words)), counts)
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.title(f'Top {top_n} Most Frequent Words - {Path(self.pdf_path).name}')
        plt.xticks(range(len(words)), words, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        
        if output_path is None:
            output_path = f"{Path(self.pdf_path).stem}_frequency_chart.png"
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def export_analysis(self, output_path: str = None) -> str:
        """Export comprehensive analysis to JSON"""
        if not self.text_data:
            self.extract_text_by_page()
        
        analysis = {
            'file_info': {
                'filename': Path(self.pdf_path).name,
                'path': str(self.pdf_path),
                'pages': len(self.doc),
                'metadata': self.metadata
            },
            'text_statistics': {
                'total_characters': len(self.extract_all_text()),
                'total_words': sum(self.get_word_frequency().values()),
                'total_sentences': self.get_sentence_count(),
                'total_paragraphs': self.get_paragraph_count(),
                'avg_words_per_page': sum(self.get_word_frequency().values()) / len(self.doc)
            },
            'word_frequency': dict(self.get_word_frequency().most_common(100)),
            'character_frequency': dict(self.get_character_frequency().most_common(50)),
            'page_statistics': self.get_page_statistics(),
            'common_phrases': dict(self.find_phrases(phrase_length=2, min_frequency=3).most_common(50))
        }
        
        if output_path is None:
            output_path = f"{Path(self.pdf_path).stem}_analysis.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()


def main():
    parser = argparse.ArgumentParser(description='PDF Text Extraction and Analysis Tool')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--extract-text', action='store_true', 
                       help='Extract and save text to file')
    parser.add_argument('--word-freq', action='store_true', 
                       help='Show word frequency analysis')
    parser.add_argument('--char-freq', action='store_true', 
                       help='Show character frequency analysis')
    parser.add_argument('--word-cloud', action='store_true', 
                       help='Generate word cloud')
    parser.add_argument('--frequency-chart', action='store_true', 
                       help='Generate frequency chart')
    parser.add_argument('--export-analysis', action='store_true', 
                       help='Export comprehensive analysis to JSON')
    parser.add_argument('--search', type=str, 
                       help='Search for specific pattern')
    parser.add_argument('--phrases', type=int, default=2, 
                       help='Find common phrases of given length')
    parser.add_argument('--min-freq', type=int, default=2, 
                       help='Minimum frequency for phrases')
    parser.add_argument('--output-dir', type=str, default='.', 
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file '{args.pdf_path}' not found")
        return 1
    
    # Create analyzer
    analyzer = PDFTextAnalyzer(args.pdf_path)
    
    if not analyzer.load_pdf():
        return 1
    
    try:
        # Extract text by page
        print(f"Extracting text from {len(analyzer.doc)} pages...")
        analyzer.extract_text_by_page()
        
        # Extract text to file if requested
        if args.extract_text:
            output_file = os.path.join(args.output_dir, 
                                     f"{Path(args.pdf_path).stem}_extracted_text.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analyzer.extract_all_text())
            print(f"Text extracted to: {output_file}")
        
        # Word frequency analysis
        if args.word_freq:
            print("\n=== WORD FREQUENCY ANALYSIS ===")
            word_freq = analyzer.get_word_frequency()
            print(f"Total unique words: {len(word_freq)}")
            print(f"Total word count: {sum(word_freq.values())}")
            print("\nTop 20 most frequent words:")
            for word, count in word_freq.most_common(20):
                print(f"  {word}: {count}")
        
        # Character frequency analysis
        if args.char_freq:
            print("\n=== CHARACTER FREQUENCY ANALYSIS ===")
            char_freq = analyzer.get_character_frequency()
            print("Top 20 most frequent characters:")
            for char, count in char_freq.most_common(20):
                print(f"  '{char}': {count}")
        
        # Generate word cloud
        if args.word_cloud:
            output_path = os.path.join(args.output_dir, 
                                     f"{Path(args.pdf_path).stem}_wordcloud.png")
            result = analyzer.generate_word_cloud(output_path)
            print(f"Word cloud generated: {result}")
        
        # Generate frequency chart
        if args.frequency_chart:
            output_path = os.path.join(args.output_dir, 
                                     f"{Path(args.pdf_path).stem}_frequency_chart.png")
            result = analyzer.create_frequency_chart(output_path)
            print(f"Frequency chart generated: {result}")
        
        # Export comprehensive analysis
        if args.export_analysis:
            output_path = os.path.join(args.output_dir, 
                                     f"{Path(args.pdf_path).stem}_analysis.json")
            result = analyzer.export_analysis(output_path)
            print(f"Analysis exported to: {result}")
        
        # Search for patterns
        if args.search:
            print(f"\n=== SEARCH RESULTS FOR '{args.search}' ===")
            matches = analyzer.search_patterns(args.search)
            print(f"Found {len(matches)} matches:")
            for i, match in enumerate(matches[:10]):  # Show first 10 matches
                print(f"  {i+1}. Page {match['page']}: {match['text']}")
                print(f"     Context: ...{match['context']}...")
        
        # Find common phrases
        if args.phrases:
            print(f"\n=== COMMON PHRASES (length {args.phrases}) ===")
            phrases = analyzer.find_phrases(phrase_length=args.phrases, 
                                         min_frequency=args.min_freq)
            print(f"Found {len(phrases)} phrases with frequency >= {args.min_freq}:")
            for phrase, count in phrases.most_common(20):
                print(f"  '{phrase}': {count}")
        
        # Show basic statistics
        print(f"\n=== BASIC STATISTICS ===")
        stats = analyzer.get_page_statistics()
        total_words = sum(page['word_count'] for page in stats.values())
        total_chars = sum(page['character_count'] for page in stats.values())
        total_sentences = sum(page['sentence_count'] for page in stats.values())
        
        print(f"Total pages: {len(analyzer.doc)}")
        print(f"Total words: {total_words}")
        print(f"Total characters: {total_chars}")
        print(f"Total sentences: {total_sentences}")
        print(f"Average words per page: {total_words / len(analyzer.doc):.1f}")
        print(f"Average characters per page: {total_chars / len(analyzer.doc):.1f}")
        print(f"Average sentences per page: {total_sentences / len(analyzer.doc):.1f}")
        
    finally:
        analyzer.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
