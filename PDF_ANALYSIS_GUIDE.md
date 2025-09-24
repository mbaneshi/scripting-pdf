# PDF Text Extraction and Analysis Tools

This toolkit provides comprehensive PDF text extraction and data analysis capabilities using `uv` for package management.

## 🚀 Quick Start

### 1. Single PDF Analysis
```bash
# Basic analysis with word frequency
uv run python pdf_text_analyzer.py "your_file.pdf" --word-freq

# Comprehensive analysis
uv run python pdf_text_analyzer.py "your_file.pdf" --word-freq --char-freq --word-cloud --frequency-chart --export-analysis

# Search for specific patterns
uv run python pdf_text_analyzer.py "your_file.pdf" --search "Heidegger"

# Find common phrases
uv run python pdf_text_analyzer.py "your_file.pdf" --phrases 3 --min-freq 5
```

### 2. Example Analysis
```bash
# Run the example script for detailed output
uv run python pdf_analyzer_example.py "your_file.pdf"
```

### 3. Batch Analysis
```bash
# Analyze all PDFs in current directory
uv run python batch_pdf_analyzer.py

# Analyze PDFs in specific directory
uv run python batch_pdf_analyzer.py --input-dir /path/to/pdfs --output-dir results
```

## 📊 Analysis Results

The tools generate several types of output:

### Text Statistics
- **Word Count**: Total and unique words
- **Character Count**: Total characters
- **Sentence Count**: Total sentences
- **Page Statistics**: Words/chars/sentences per page
- **Readability Metrics**: Average words per sentence

### Frequency Analysis
- **Word Frequency**: Most common words
- **Character Frequency**: Most common characters
- **Phrase Analysis**: Common n-grams (2-word, 3-word phrases)
- **Pattern Search**: Find specific text patterns

### Visualizations
- **Word Clouds**: Visual representation of word frequency
- **Frequency Charts**: Bar charts of top words
- **Comparative Charts**: Multi-PDF comparisons

### Export Formats
- **JSON**: Complete analysis data
- **CSV**: Tabular data for spreadsheet analysis
- **TXT**: Human-readable reports
- **PNG**: Visualization images

## 🔧 Available Tools

### 1. `pdf_text_analyzer.py`
Main analysis tool with comprehensive features:
- Text extraction by page or entire document
- Word and character frequency analysis
- Pattern searching and phrase detection
- Visualization generation (word clouds, charts)
- Export capabilities (JSON, images)

### 2. `pdf_analyzer_example.py`
User-friendly example script:
- Clean, formatted output
- Basic statistics overview
- Top words and phrases
- Page-by-page breakdown
- Automatic file generation

### 3. `batch_pdf_analyzer.py`
Batch processing tool:
- Analyze multiple PDFs simultaneously
- Comparative analysis across documents
- Statistical summaries
- Comparative visualizations
- Comprehensive reporting

## 📈 Sample Results

From analyzing "Speaking Being" (579 pages):
- **Total Words**: 253,162
- **Unique Words**: 11,702
- **Most Common Words**: "the" (11,710), "and" (6,325), "you" (6,094)
- **Common Phrases**: "in the" (1,275), "of the" (1,198), "to be" (917)
- **Average Words/Page**: 437.2
- **Average Words/Sentence**: 12.6

## 🎯 Use Cases

### Academic Research
- Analyze philosophical texts for terminology frequency
- Compare writing styles across documents
- Extract key concepts and themes

### Content Analysis
- Identify common phrases and patterns
- Measure readability and complexity
- Track word usage trends

### Data Mining
- Extract structured data from PDFs
- Generate insights from document collections
- Create searchable text databases

## 🛠️ Dependencies

All dependencies are managed with `uv`:
- **PyMuPDF**: PDF text extraction
- **Matplotlib**: Data visualization
- **Seaborn**: Statistical plotting
- **Pandas**: Data manipulation
- **WordCloud**: Word cloud generation

## 📁 Output Structure

```
analysis_output/
├── comparative_analysis_report.txt    # Human-readable summary
├── comparative_analysis.csv          # Tabular data
├── comparative_charts.png            # Visualization charts
└── all_analysis_results.json        # Complete data export
```

## 🔍 Advanced Features

### Custom Analysis
```python
from pdf_text_analyzer import PDFTextAnalyzer

analyzer = PDFTextAnalyzer("document.pdf")
analyzer.load_pdf()
analyzer.extract_text_by_page()

# Custom word frequency with filters
word_freq = analyzer.get_word_frequency(min_length=4, case_sensitive=False)

# Search for specific patterns
matches = analyzer.search_patterns(r"\b[A-Z][a-z]+\b")  # Find capitalized words
```

### Batch Processing
```python
from batch_pdf_analyzer import BatchPDFAnalyzer

batch = BatchPDFAnalyzer(input_dir="pdfs/", output_dir="results/")
results = batch.analyze_all_pdfs()
report = batch.generate_comparative_report()
```

## 📝 Notes

- All tools use UTF-8 encoding for proper text handling
- Large PDFs may take time to process
- Visualizations require display capabilities
- Results are saved automatically to specified directories
- Tools handle various PDF formats and encodings

