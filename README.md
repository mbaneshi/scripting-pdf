# AI-Powered PDF Translation Pipeline

A sophisticated multi-agent translation system for converting English academic texts to Farsi with pixel-perfect preservation and terminology consistency.

## 🎯 Features

- **Multi-Agent Translation**: Specialized AI agents for different translation tasks
- **Intelligent Chapter Extraction**: Automatically groups pages into logical chapters
- **Database Persistence**: PostgreSQL storage for all translation metadata
- **File-Based Workflow**: Both database and file system storage
- **Terminology Consistency**: Maintains academic glossary across translations
- **Quality Assurance**: Multi-stage review and consistency checking
- **Farsi Font Support**: Vazirmatn font integration for proper RTL text

## 🏗️ Architecture

### Core Components

1. **Chapter Extractor** (`chapter_extractor.py`)
   - Analyzes page content to identify chapter boundaries
   - Groups pages into logical chapters
   - Extracts metadata and content structure

2. **Multi-Agent Pipeline** (`multi_agent_pipeline.py`)
   - **Content Analyzer**: Identifies structure and themes
   - **Terminology Specialist**: Ensures consistent term translation
   - **Primary Translator**: Performs high-quality translation
   - **Quality Reviewer**: Reviews and improves translations
   - **Consistency Checker**: Ensures uniformity across chapters

3. **Enhanced Database** (`enhanced_database.py`)
   - PostgreSQL schema for chapters, chunks, and translations
   - Terminology database for consistency
   - Translation job tracking and quality metrics

4. **Pipeline Orchestrator** (`pipeline_orchestrator.py`)
   - Coordinates all components
   - Manages the complete workflow
   - Creates final outputs

### Database Schema

```sql
-- Core tables
pdf_documents     # Document metadata
chapters         # Chapter information and content
text_chunks      # Text segments for processing
translation_jobs # Translation tracking and quality
terminology_database # Consistent terminology
pdf_pages        # Individual page data
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (Docker)
- OpenAI API key
- `uv` package manager

### Installation

```bash
# Clone and setup
git clone <repository>
cd scripting-pdf

# Install dependencies
uv sync

# Start PostgreSQL
docker-compose up -d

# Set environment variables
export OPENAI_API_KEY="your-api-key"
```

### Basic Usage

```bash
# 1. Extract pages from PDF
uv run python extract_all_pages.py "your-document.pdf"

# 2. Extract chapters from pages
uv run python chapter_extractor.py

# 3. Run complete translation pipeline
uv run python pipeline_orchestrator.py --openai-key "your-api-key"
```

## 📁 File Structure

```
scripting-pdf/
├── simple_pages/              # Extracted page files
├── chapters/                  # Chapter files (EN + FA)
├── translated_pages/          # Individual page translations
├── final_outputs/            # Final documents
├── database/                 # PostgreSQL database
├── extract_all_pages.py     # PDF page extraction
├── chapter_extractor.py     # Chapter grouping
├── multi_agent_pipeline.py   # AI translation pipeline
├── pipeline_orchestrator.py  # Main orchestrator
├── enhanced_database.py      # Database models
└── docker-compose.yml        # Database setup
```

## 🔧 Advanced Usage

### Chapter-Only Extraction

```bash
# Extract chapters without translation
uv run python pipeline_orchestrator.py --extract-only
```

### Translation-Only Mode

```bash
# Translate existing chapters
uv run python pipeline_orchestrator.py --translate-only
```

### Custom Configuration

```bash
# Custom pages directory
uv run python pipeline_orchestrator.py --pages-dir "custom_pages"

# Custom document ID
uv run python pipeline_orchestrator.py --document-id 2
```

## 🤖 Multi-Agent Translation Process

### Agent Roles

1. **Content Analyzer**
   - Identifies text structure and themes
   - Assesses translation complexity
   - Recommends chunking strategy

2. **Terminology Specialist**
   - Extracts specialized terms
   - Maintains consistency
   - Handles philosophical concepts

3. **Primary Translator**
   - Performs high-quality translation
   - Maintains academic tone
   - Preserves original meaning

4. **Quality Reviewer**
   - Reviews translation accuracy
   - Improves fluency
   - Ensures terminology consistency

5. **Consistency Checker**
   - Ensures uniform style
   - Catches inconsistencies
   - Maintains document coherence

### Translation Workflow

```
PDF → Pages → Chapters → Chunks → Translation → Review → Consistency → Final Output
```

## 📊 Quality Metrics

- **Confidence Score**: AI translation confidence
- **Terminology Score**: Consistency of specialized terms
- **Fluency Score**: Natural Farsi expression
- **Overall Quality**: Composite quality rating

## 🎨 Farsi Font Integration

- **Primary Font**: Vazirmatn
- **RTL Support**: Right-to-left text handling
- **Character Reshaping**: Arabic character shaping
- **Layout Preservation**: Pixel-perfect positioning

## 🔍 Monitoring and Debugging

### Progress Tracking

```bash
# View translation progress
cat final_outputs/translation_progress_report.txt

# Check file structure
cat final_outputs/file_structure_summary.txt
```

### Database Queries

```python
from enhanced_database import get_chapters_by_document, get_chunks_by_chapter

# Get all chapters
chapters = get_chapters_by_document(1)

# Get chapter chunks
chunks = get_chunks_by_chapter(chapter_id)
```

## 🚨 Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

2. **Database Connection Failed**
   ```bash
   docker-compose up -d
   ```

3. **Memory Issues with Large Documents**
   - Reduce chunk size in `multi_agent_pipeline.py`
   - Process chapters individually

### Error Handling

- All components include comprehensive error handling
- Failed translations are logged and can be retried
- Database transactions ensure data consistency

## 🔮 Future Enhancements

- **Vector Database**: ChromaDB for semantic search
- **RAG Integration**: Retrieval-augmented generation
- **Batch Processing**: Parallel chapter translation
- **Web Interface**: Streamlit dashboard
- **API Endpoints**: RESTful API for integration

## 📝 License

This project is for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review error logs
- Open an issue on GitHub