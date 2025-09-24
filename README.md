# PDF Translation SaaS Platform

A modern AI-powered PDF translation service built with Streamlit, PostgreSQL, and AI APIs.

## Features

- PDF text extraction using PyMuPDF
- PostgreSQL database for persistence
- Streamlit web interface
- Dockerized PostgreSQL setup
- Ready for AI API integration

## Quick Start

1. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

2. **Run the Streamlit app**:
   ```bash
   uv run streamlit run app.py
   ```

3. **Access the app**: http://localhost:8501

## Project Structure

- `app.py` - Main Streamlit application
- `database.py` - Database models and operations
- `pdf_extractor.py` - PDF text extraction utilities
- `docker-compose.yml` - PostgreSQL container setup
