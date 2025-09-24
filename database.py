import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres123@localhost:5463/pdf_translation"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PDFDocument(Base):
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    page_count = Column(Integer)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)

class PDFPage(Base):
    __tablename__ = "pdf_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("pdf_documents.id"))
    page_number = Column(Integer, nullable=False)
    
    # Extracted content
    original_text = Column(Text)
    text_blocks = Column(JSON)  # Text with positioning, fonts, styles
    layout_info = Column(JSON)  # Margins, columns, positioning
    fonts_used = Column(JSON)   # Font information
    images_info = Column(JSON)  # Image positions and references
    
    # File paths for manual workflow
    original_text_file = Column(String(255))  # Path to text file
    translated_text_file = Column(String(255))  # Path to translated file
    
    # Processing status
    extracted = Column(Boolean, default=False)
    ready_for_translation = Column(Boolean, default=False)
    translated = Column(Boolean, default=False)
    pdf_reconstructed = Column(Boolean, default=False)
    
    # Timestamps
    extracted_at = Column(DateTime)
    translated_at = Column(DateTime)
    reconstructed_at = Column(DateTime)

class TranslationJob(Base):
    __tablename__ = "translation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pdf_pages.id"))
    
    # Translation content
    original_text = Column(Text)
    translated_text = Column(Text)
    
    # Manual translation metadata
    translator = Column(String(50), default="AI Assistant")
    translation_date = Column(DateTime, default=datetime.utcnow)
    quality_rating = Column(Integer)  # 1-5 rating
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, in_progress, completed, reviewed
    notes = Column(Text)  # Translation notes or issues
    
    # File management
    original_file_path = Column(String(255))
    translated_file_path = Column(String(255))

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_pdf_document(filename, file_size, page_count):
    """Save PDF document metadata to database"""
    db = SessionLocal()
    try:
        document = PDFDocument(
            filename=filename,
            file_size=file_size,
            page_count=page_count,
            processed=True
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def save_pdf_page(document_id, page_number, text, text_blocks, layout_info, fonts_used, images_info, text_file_path):
    """Save individual PDF page data to database"""
    db = SessionLocal()
    try:
        page = PDFPage(
            document_id=document_id,
            page_number=page_number,
            original_text=text,
            text_blocks=text_blocks,
            layout_info=layout_info,
            fonts_used=fonts_used,
            images_info=images_info,
            original_text_file=text_file_path,
            extracted=True,
            ready_for_translation=True,
            extracted_at=datetime.utcnow()
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return page.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_documents():
    """Get all PDF documents from database"""
    db = SessionLocal()
    try:
        return db.query(PDFDocument).all()
    finally:
        db.close()

def get_document_by_id(doc_id):
    """Get specific document by ID"""
    db = SessionLocal()
    try:
        return db.query(PDFDocument).filter(PDFDocument.id == doc_id).first()
    finally:
        db.close()

def get_pages_by_document(document_id):
    """Get all pages for a specific document"""
    db = SessionLocal()
    try:
        return db.query(PDFPage).filter(PDFPage.document_id == document_id).order_by(PDFPage.page_number).all()
    finally:
        db.close()

def get_page_by_id(page_id):
    """Get specific page by ID"""
    db = SessionLocal()
    try:
        return db.query(PDFPage).filter(PDFPage.id == page_id).first()
    finally:
        db.close()

def get_pages_ready_for_translation(document_id=None, limit=50):
    """Get pages ready for translation"""
    db = SessionLocal()
    try:
        query = db.query(PDFPage).filter(
            PDFPage.extracted == True,
            PDFPage.ready_for_translation == True,
            PDFPage.translated == False
        )
        
        if document_id:
            query = query.filter(PDFPage.document_id == document_id)
        
        return query.order_by(PDFPage.page_number).limit(limit).all()
    finally:
        db.close()

def save_translation_job(page_id, original_text, translated_text, translator="AI Assistant", notes=""):
    """Save translation job to database"""
    db = SessionLocal()
    try:
        # Update page status
        page = db.query(PDFPage).filter(PDFPage.id == page_id).first()
        if page:
            page.translated = True
            page.translated_at = datetime.utcnow()
        
        # Create translation job
        job = TranslationJob(
            page_id=page_id,
            original_text=original_text,
            translated_text=translated_text,
            translator=translator,
            status="completed",
            notes=notes
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
