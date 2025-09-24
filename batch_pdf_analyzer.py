#!/usr/bin/env python3
"""
Batch PDF Analysis Tool
Analyzes multiple PDF files and generates comparative reports
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from pdf_text_analyzer import PDFTextAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns

class BatchPDFAnalyzer:
    """Batch analysis of multiple PDF files"""
    
    def __init__(self, input_dir: str = ".", output_dir: str = "analysis_output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.results = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def find_pdf_files(self) -> list:
        """Find all PDF files in input directory"""
        pdf_files = []
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files
    
    def analyze_single_pdf(self, pdf_path: str) -> dict:
        """Analyze a single PDF file"""
        print(f"Analyzing: {Path(pdf_path).name}")
        
        analyzer = PDFTextAnalyzer(pdf_path)
        if not analyzer.load_pdf():
            return None
        
        try:
            analyzer.extract_text_by_page()
            
            # Get basic statistics
            stats = analyzer.get_page_statistics()
            word_freq = analyzer.get_word_frequency()
            char_freq = analyzer.get_character_frequency()
            
            # Calculate totals
            total_words = sum(page['word_count'] for page in stats.values())
            total_chars = sum(page['character_count'] for page in stats.values())
            total_sentences = sum(page['sentence_count'] for page in stats.values())
            
            result = {
                'filename': Path(pdf_path).name,
                'filepath': pdf_path,
                'pages': len(analyzer.doc),
                'total_words': total_words,
                'total_characters': total_chars,
                'total_sentences': total_sentences,
                'unique_words': len(word_freq),
                'avg_words_per_page': total_words / len(analyzer.doc) if analyzer.doc else 0,
                'avg_chars_per_page': total_chars / len(analyzer.doc) if analyzer.doc else 0,
                'avg_sentences_per_page': total_sentences / len(analyzer.doc) if analyzer.doc else 0,
                'avg_words_per_sentence': total_words / max(total_sentences, 1),
                'top_words': dict(word_freq.most_common(20)),
                'top_characters': dict(char_freq.most_common(10)),
                'page_stats': stats
            }
            
            return result
            
        finally:
            analyzer.close()
    
    def analyze_all_pdfs(self) -> list:
        """Analyze all PDF files in input directory"""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            print("No PDF files found!")
            return []
        
        print(f"Found {len(pdf_files)} PDF files to analyze")
        
        results = []
        for pdf_path in pdf_files:
            result = self.analyze_single_pdf(pdf_path)
            if result:
                results.append(result)
                self.results.append(result)
        
        return results
    
    def generate_comparative_report(self) -> str:
        """Generate comparative analysis report"""
        if not self.results:
            return "No results to report"
        
        # Create DataFrame for analysis
        df_data = []
        for result in self.results:
            df_data.append({
                'Filename': result['filename'],
                'Pages': result['pages'],
                'Total Words': result['total_words'],
                'Total Characters': result['total_characters'],
                'Total Sentences': result['total_sentences'],
                'Unique Words': result['unique_words'],
                'Avg Words/Page': result['avg_words_per_page'],
                'Avg Chars/Page': result['avg_chars_per_page'],
                'Avg Sentences/Page': result['avg_sentences_per_page'],
                'Avg Words/Sentence': result['avg_words_per_sentence']
            })
        
        df = pd.DataFrame(df_data)
        
        # Save detailed report
        report_file = os.path.join(self.output_dir, "comparative_analysis_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("PDF COMPARATIVE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total PDFs analyzed: {len(self.results)}\n")
            f.write(f"Total pages: {sum(r['pages'] for r in self.results):,}\n")
            f.write(f"Total words: {sum(r['total_words'] for r in self.results):,}\n")
            f.write(f"Total characters: {sum(r['total_characters'] for r in self.results):,}\n")
            f.write(f"Total sentences: {sum(r['total_sentences'] for r in self.results):,}\n\n")
            
            f.write("PER-FILE BREAKDOWN:\n")
            f.write("-" * 20 + "\n")
            for result in self.results:
                f.write(f"\nFile: {result['filename']}\n")
                f.write(f"  Pages: {result['pages']:,}\n")
                f.write(f"  Words: {result['total_words']:,}\n")
                f.write(f"  Characters: {result['total_characters']:,}\n")
                f.write(f"  Sentences: {result['total_sentences']:,}\n")
                f.write(f"  Unique words: {result['unique_words']:,}\n")
                f.write(f"  Avg words/page: {result['avg_words_per_page']:.1f}\n")
                f.write(f"  Avg chars/page: {result['avg_chars_per_page']:.1f}\n")
                f.write(f"  Avg sentences/page: {result['avg_sentences_per_page']:.1f}\n")
                f.write(f"  Avg words/sentence: {result['avg_words_per_sentence']:.1f}\n")
            
            f.write("\nSTATISTICAL SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Average pages per file: {df['Pages'].mean():.1f}\n")
            f.write(f"Average words per file: {df['Total Words'].mean():.1f}\n")
            f.write(f"Average characters per file: {df['Total Characters'].mean():.1f}\n")
            f.write(f"Average sentences per file: {df['Total Sentences'].mean():.1f}\n")
            f.write(f"Average unique words per file: {df['Unique Words'].mean():.1f}\n")
        
        # Save CSV
        csv_file = os.path.join(self.output_dir, "comparative_analysis.csv")
        df.to_csv(csv_file, index=False)
        
        # Generate visualizations
        self.create_comparative_charts(df)
        
        return report_file
    
    def create_comparative_charts(self, df: pd.DataFrame):
        """Create comparative visualization charts"""
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('PDF Analysis Comparative Charts', fontsize=16, fontweight='bold')
        
        # Chart 1: Pages comparison
        axes[0, 0].bar(range(len(df)), df['Pages'])
        axes[0, 0].set_title('Pages per PDF')
        axes[0, 0].set_xlabel('PDF Files')
        axes[0, 0].set_ylabel('Number of Pages')
        axes[0, 0].set_xticks(range(len(df)))
        axes[0, 0].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        # Chart 2: Words comparison
        axes[0, 1].bar(range(len(df)), df['Total Words'])
        axes[0, 1].set_title('Total Words per PDF')
        axes[0, 1].set_xlabel('PDF Files')
        axes[0, 1].set_ylabel('Number of Words')
        axes[0, 1].set_xticks(range(len(df)))
        axes[0, 1].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        # Chart 3: Characters comparison
        axes[0, 2].bar(range(len(df)), df['Total Characters'])
        axes[0, 2].set_title('Total Characters per PDF')
        axes[0, 2].set_xlabel('PDF Files')
        axes[0, 2].set_ylabel('Number of Characters')
        axes[0, 2].set_xticks(range(len(df)))
        axes[0, 2].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        # Chart 4: Words per page
        axes[1, 0].bar(range(len(df)), df['Avg Words/Page'])
        axes[1, 0].set_title('Average Words per Page')
        axes[1, 0].set_xlabel('PDF Files')
        axes[1, 0].set_ylabel('Words per Page')
        axes[1, 0].set_xticks(range(len(df)))
        axes[1, 0].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        # Chart 5: Unique words ratio
        unique_ratio = df['Unique Words'] / df['Total Words']
        axes[1, 1].bar(range(len(df)), unique_ratio)
        axes[1, 1].set_title('Unique Words Ratio')
        axes[1, 1].set_xlabel('PDF Files')
        axes[1, 1].set_ylabel('Unique Words / Total Words')
        axes[1, 1].set_xticks(range(len(df)))
        axes[1, 1].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        # Chart 6: Words per sentence
        axes[1, 2].bar(range(len(df)), df['Avg Words/Sentence'])
        axes[1, 2].set_title('Average Words per Sentence')
        axes[1, 2].set_xlabel('PDF Files')
        axes[1, 2].set_ylabel('Words per Sentence')
        axes[1, 2].set_xticks(range(len(df)))
        axes[1, 2].set_xticklabels([f.split('.')[0][:10] for f in df['Filename']], 
                                  rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the chart
        chart_file = os.path.join(self.output_dir, "comparative_charts.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comparative charts saved to: {chart_file}")
    
    def export_all_results(self) -> str:
        """Export all analysis results to JSON"""
        output_file = os.path.join(self.output_dir, "all_analysis_results.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return output_file


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch PDF Analysis Tool')
    parser.add_argument('--input-dir', default='.', 
                       help='Input directory containing PDF files')
    parser.add_argument('--output-dir', default='analysis_output', 
                       help='Output directory for analysis results')
    
    args = parser.parse_args()
    
    print("PDF Batch Analysis Tool")
    print("=" * 30)
    
    # Create batch analyzer
    batch_analyzer = BatchPDFAnalyzer(args.input_dir, args.output_dir)
    
    # Analyze all PDFs
    results = batch_analyzer.analyze_all_pdfs()
    
    if not results:
        print("No PDF files found or analyzed successfully")
        return 1
    
    print(f"\nSuccessfully analyzed {len(results)} PDF files")
    
    # Generate comparative report
    print("\nGenerating comparative report...")
    report_file = batch_analyzer.generate_comparative_report()
    print(f"Report saved to: {report_file}")
    
    # Export all results
    print("\nExporting all results...")
    json_file = batch_analyzer.export_all_results()
    print(f"All results exported to: {json_file}")
    
    print(f"\nAll analysis files saved in: {args.output_dir}")
    print("✅ Batch analysis complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

