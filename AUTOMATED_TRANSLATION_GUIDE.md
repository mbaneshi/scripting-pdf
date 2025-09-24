# 🤖 Automated Translation System Guide

This guide covers the complete automated translation workflow for PDF sections using the `automated_translator.py` script.

## 🎯 Overview

The automated translation system processes extracted PDF sections and translates them to Farsi using Google Translate via the `deep-translator` library. It handles:

- ✅ **Text extraction** from markdown files
- ✅ **Automatic translation** to Farsi
- ✅ **Progress tracking** and error handling
- ✅ **Rate limiting** to avoid API limits
- ✅ **Batch processing** of multiple files
- ✅ **Index generation** for translated files
- ✅ **Statistics tracking** and reporting

## 🚀 Quick Start

### 1. **Prerequisites**
```bash
# Install required packages
uv pip install deep-translator
```

### 2. **Basic Usage**
```bash
# Translate all files in a directory
uv run python automated_translator.py toc_sections --output-dir farsi_translations

# Translate only first 5 files (for testing)
uv run python automated_translator.py toc_sections --max-files 5

# Translate a single file
uv run python automated_translator.py toc_sections --single-file toc_sections/008_Talking_about_Being.md
```

## 📋 Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `input_dir` | Directory containing markdown files | `toc_sections` |
| `--output-dir` | Output directory for Farsi translations | `--output-dir farsi_translations` |
| `--max-files` | Maximum number of files to process | `--max-files 10` |
| `--single-file` | Process only a specific file | `--single-file path/to/file.md` |

## 🔄 Complete Workflow Example

### Step 1: Extract Sections from PDF
```bash
# Extract sections using TOC-based method (recommended)
uv run python toc_based_extractor.py "your_book.pdf" --toc-page 9 --output-dir toc_sections

# Or extract Forum sessions
uv run python forum_session_extractor.py "your_book.pdf" --output-dir forum_sessions
```

### Step 2: Translate Sections
```bash
# Translate all extracted sections
uv run python automated_translator.py toc_sections --output-dir farsi_translations

# Or translate Forum sessions
uv run python automated_translator.py forum_sessions --output-dir farsi_forum_translations
```

### Step 3: Review Results
```bash
# Check the index file
cat farsi_translations/00_FARSI_TRANSLATIONS_INDEX.md

# View translation statistics
cat farsi_translations/translation_stats.json
```

## 📁 Output Structure

### Generated Files:
```
farsi_translations/
├── 00_FARSI_TRANSLATIONS_INDEX.md    # Index of all translations
├── translation_stats.json            # Translation statistics
├── 008_Talking_about_Being_farsi.md  # Individual translations
├── 012_Dasein_farsi.md
├── 014_Two_Theses_farsi.md
└── ...
```

### Translation File Format:
Each translated file contains:
- **Farsi header** with original title
- **Metadata section** with translation info
- **Original content** for reference
- **Translated content** in Farsi

## 📊 Translation Statistics

The system tracks:
- **Total files** processed
- **Successfully translated** files
- **Failed translations**
- **Processing time**
- **Success rate**

Example output:
```
📊 TRANSLATION SUMMARY
==================================================
Total files: 59
Processed: 59
Failed: 0
Success rate: 100.0%
Duration: 0:05:23.456789
```

## ⚙️ Advanced Features

### 1. **Text Chunking**
- Automatically splits long texts (>4000 chars)
- Respects sentence boundaries
- Handles rate limiting

### 2. **Error Handling**
- Retry mechanism (3 attempts)
- Exponential backoff
- Graceful failure handling

### 3. **Progress Tracking**
- Real-time progress updates
- Processing time estimation
- Success/failure reporting

### 4. **Rate Limiting**
- Built-in delays between requests
- Prevents API rate limit issues
- Configurable timing

## 🎯 Best Practices

### 1. **Testing First**
```bash
# Always test with a few files first
uv run python automated_translator.py toc_sections --max-files 3
```

### 2. **Batch Processing**
```bash
# Process in smaller batches for large datasets
uv run python automated_translator.py toc_sections --max-files 20
```

### 3. **Monitoring Progress**
- Watch for error messages
- Check success rates
- Monitor processing time

### 4. **Quality Control**
- Review sample translations
- Check for missing content
- Verify formatting

## 🔧 Troubleshooting

### Common Issues:

1. **Translation Service Unavailable**
   ```
   ❌ Deep Translator not available
   ```
   **Solution**: Install deep-translator
   ```bash
   uv pip install deep-translator
   ```

2. **Rate Limiting**
   ```
   ⚠️ Translation attempt 1 failed: Rate limit exceeded
   ```
   **Solution**: Script automatically retries with backoff

3. **Empty Content**
   ```
   ⚠️ No content found in file
   ```
   **Solution**: Check markdown file format

4. **Network Issues**
   ```
   ⚠️ Translation attempt failed: Connection error
   ```
   **Solution**: Check internet connection, script will retry

## 📈 Performance Tips

1. **Use TOC-based extraction** for clean, organized sections
2. **Process in batches** to avoid overwhelming the translation service
3. **Monitor success rates** to catch issues early
4. **Check sample translations** for quality assurance

## 🎯 Integration with Other Tools

### Combine with Text Analysis:
```bash
# Extract and analyze
uv run python toc_based_extractor.py "book.pdf" --output-dir sections
uv run python pdf_text_analyzer.py "book.pdf" --word-freq --export-analysis

# Translate sections
uv run python automated_translator.py sections --output-dir farsi_sections
```

### Batch Processing Multiple PDFs:
```bash
# Process multiple books
for pdf in *.pdf; do
  uv run python toc_based_extractor.py "$pdf" --output-dir "sections_${pdf%.pdf}"
  uv run python automated_translator.py "sections_${pdf%.pdf}" --output-dir "farsi_${pdf%.pdf}"
done
```

## 📚 Example Results

### Sample Translation Output:
```markdown
# Talking about Being (فارسی)

## 📋 اطلاعات بخش
- **عنوان**: Talking about Being
- **صفحه**: 8
- **منبع**: Bruce_Hyde,_Drew_Kopp_Speaking_Being_Werner_Erhard,_Martin_Heidegger (1).pdf
- **تاریخ ترجمه**: 2025-09-24 14:58:12

## 📄 محتوای ترجمه شده
مطالب
ششم
مطالب
درباره نویسندگان
IX
مقدمه
...
```

This automated translation system provides a complete solution for translating PDF sections to Farsi with professional quality and comprehensive tracking!

