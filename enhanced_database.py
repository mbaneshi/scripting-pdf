import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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
    
    # Relationships
    chapters = relationship("Chapter", back_populates="document")
    pages = relationship("PDFPage", back_populates="document")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("pdf_documents.id"))
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500))
    
    # Content management
    start_page = Column(Integer)
    end_page = Column(Integer)
    total_pages = Column(Integer)
    
    # Text content
    original_text = Column(Text)
    farsi_text = Column(Text)
    
    # File paths
    original_file_path = Column(String(500))
    farsi_file_path = Column(String(500))
    
    # Processing status
    extracted = Column(Boolean, default=False)
    chunked = Column(Boolean, default=False)
    translated = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    
    # Quality metrics
    translation_quality_score = Column(Float)
    consistency_score = Column(Float)
    
    # Timestamps
    extracted_at = Column(DateTime)
    translated_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    
    # Relationships
    document = relationship("PDFDocument", back_populates="chapters")
    chunks = relationship("TextChunk", back_populates="chapter")
    translations = relationship("TranslationJob", back_populates="chapter")

class TextChunk(Base):
    __tablename__ = "text_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    chunk_number = Column(Integer, nullable=False)
    
    # Content
    original_text = Column(Text)
    farsi_text = Column(Text)
    
    # Metadata
    chunk_size = Column(Integer)  # Character count
    token_count = Column(Integer)
    page_references = Column(JSON)  # Which pages this chunk covers
    
    # Processing status
    translated = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    
    # Quality metrics
    translation_confidence = Column(Float)
    terminology_consistency = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    translated_at = Column(DateTime)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="chunks")
    translations = relationship("TranslationJob", back_populates="chunk")

class TranslationJob(Base):
    __tablename__ = "translation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    chunk_id = Column(Integer, ForeignKey("text_chunks.id"))
    
    # Agent information
    agent_name = Column(String(100))  # Which agent performed translation
    agent_role = Column(String(100))  # Role of the agent
    
    # Translation content
    original_text = Column(Text)
    translated_text = Column(Text)
    
    # AI processing details
    model_used = Column(String(100))
    prompt_template = Column(String(200))
    temperature = Column(Float)
    max_tokens = Column(Integer)
    
    # Quality metrics
    confidence_score = Column(Float)
    terminology_score = Column(Float)
    fluency_score = Column(Float)
    overall_quality = Column(Float)
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, processing, completed, failed, reviewed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="translations")
    chunk = relationship("TextChunk", back_populates="translations")

class TerminologyDatabase(Base):
    __tablename__ = "terminology_database"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core terms
    english_term = Column(String(300), nullable=False)
    farsi_term = Column(String(300), nullable=False)
    
    # Context and usage
    context_type = Column(String(100))  # "heidegger", "erhard", "philosophical", "general"
    domain = Column(String(100))  # "ontology", "authenticity", "being", etc.
    
    # Usage tracking
    usage_count = Column(Integer, default=1)
    confidence_score = Column(Float)
    verified_by_human = Column(Boolean, default=False)
    
    # Context examples
    context_examples = Column(JSON)  # Sample sentences using the term
    translation_examples = Column(JSON)  # Previous translations
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Quality
    quality_rating = Column(Integer)  # 1-5 rating

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
    
    # Relationships
    document = relationship("PDFDocument", back_populates="pages")

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

# Enhanced functions for chapter-based processing
def save_chapter(document_id, chapter_number, title, start_page, end_page, original_text, file_path):
    """Save chapter data to database"""
    db = SessionLocal()
    try:
        chapter = Chapter(
            document_id=document_id,
            chapter_number=chapter_number,
            title=title,
            start_page=start_page,
            end_page=end_page,
            total_pages=end_page - start_page + 1,
            original_text=original_text,
            original_file_path=file_path,
            extracted=True,
            extracted_at=datetime.utcnow()
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        return chapter.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def save_text_chunk(chapter_id, chunk_number, original_text, chunk_size, token_count, page_references):
    """Save text chunk to database"""
    db = SessionLocal()
    try:
        chunk = TextChunk(
            chapter_id=chapter_id,
            chunk_number=chunk_number,
            original_text=original_text,
            chunk_size=chunk_size,
            token_count=token_count,
            page_references=page_references,
            created_at=datetime.utcnow()
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def save_translation_job(chapter_id, chunk_id, agent_name, agent_role, original_text, translated_text, 
                        model_used, confidence_score, status="completed"):
    """Save translation job to database"""
    db = SessionLocal()
    try:
        job = TranslationJob(
            chapter_id=chapter_id,
            chunk_id=chunk_id,
            agent_name=agent_name,
            agent_role=agent_role,
            original_text=original_text,
            translated_text=translated_text,
            model_used=model_used,
            confidence_score=confidence_score,
            status=status,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if status == "completed" else None
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

def get_chapters_by_document(document_id):
    """Get all chapters for a document"""
    db = SessionLocal()
    try:
        return db.query(Chapter).filter(Chapter.document_id == document_id).order_by(Chapter.chapter_number).all()
    finally:
        db.close()

def get_chunks_by_chapter(chapter_id):
    """Get all chunks for a chapter"""
    db = SessionLocal()
    try:
        return db.query(TextChunk).filter(TextChunk.chapter_id == chapter_id).order_by(TextChunk.chunk_number).all()
    finally:
        db.close()

def get_translation_jobs_by_chapter(chapter_id):
    """Get all translation jobs for a chapter"""
    db = SessionLocal()
    try:
        return db.query(TranslationJob).filter(TranslationJob.chapter_id == chapter_id).all()
    finally:
        db.close()
