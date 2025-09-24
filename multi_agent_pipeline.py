#!/usr/bin/env python3
"""
Multi-Agent Translation Pipeline using CrewAI
Precise translation with specialized agents for different tasks
"""

import os
import json
import tiktoken
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from enhanced_database import (
    create_tables, save_chapter, save_text_chunk, save_translation_job,
    get_chapters_by_document, get_chunks_by_chapter, get_translation_jobs_by_chapter
)

class MultiAgentTranslationPipeline:
    def __init__(self, openai_api_key: str = None):
        """Initialize the multi-agent translation pipeline"""
        
        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize models
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=4000
        )
        
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize vector store for terminology
        self.vector_store = Chroma(
            collection_name="terminology",
            embedding_function=self.embeddings
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Token counter
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Create specialized agents
        self._create_agents()
        
        # Initialize database
        create_tables()
    
    def _create_agents(self):
        """Create specialized translation agents"""
        
        # 1. Content Analyzer Agent
        self.content_analyzer = Agent(
            role="Content Analyzer",
            goal="Analyze text content to identify structure, themes, and translation requirements",
            backstory="""You are an expert content analyst specializing in philosophical and academic texts. 
            You excel at identifying text structure, themes, terminology, and translation complexity.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 2. Terminology Specialist Agent
        self.terminology_specialist = Agent(
            role="Terminology Specialist",
            goal="Ensure consistent and accurate translation of specialized terms",
            backstory="""You are a terminology expert specializing in Heideggerian and Erhardian philosophy. 
            You maintain consistency in philosophical terms and ensure accurate academic translation.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 3. Primary Translator Agent
        self.primary_translator = Agent(
            role="Primary Translator",
            goal="Translate English text to Farsi with high accuracy and fluency",
            backstory="""You are a professional translator specializing in academic and philosophical texts. 
            You translate with precision while maintaining the original meaning and academic tone.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 4. Quality Reviewer Agent
        self.quality_reviewer = Agent(
            role="Quality Reviewer",
            goal="Review and improve translation quality, consistency, and accuracy",
            backstory="""You are a quality assurance expert specializing in Farsi translations. 
            You ensure translations are accurate, fluent, and consistent with established terminology.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 5. Consistency Checker Agent
        self.consistency_checker = Agent(
            role="Consistency Checker",
            goal="Ensure terminology and style consistency across all translations",
            backstory="""You are a consistency expert who ensures all translations maintain uniform terminology 
            and style throughout the document. You catch inconsistencies and suggest improvements.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content structure and requirements"""
        
        task = Task(
            description=f"""
            Analyze the following text and provide:
            1. Text structure (paragraphs, sections, dialogue, etc.)
            2. Key themes and concepts
            3. Specialized terminology
            4. Translation complexity assessment
            5. Recommended chunking strategy
            
            Text to analyze:
            {text[:1000]}...
            """,
            agent=self.content_analyzer,
            expected_output="JSON analysis with structure, themes, terminology, and recommendations"
        )
        
        crew = Crew(
            agents=[self.content_analyzer],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return json.loads(str(result))
    
    def extract_terminology(self, text: str) -> List[Dict[str, str]]:
        """Extract and standardize terminology"""
        
        task = Task(
            description=f"""
            Extract specialized terminology from this text and provide standardized translations:
            
            Text: {text[:1500]}...
            
            Focus on:
            - Philosophical terms (Heidegger, Erhard concepts)
            - Academic terminology
            - Technical terms
            - Proper nouns
            
            Provide format: [{{"english": "term", "farsi": "ترجمه", "context": "explanation"}}]
            """,
            agent=self.terminology_specialist,
            expected_output="List of terminology with English-Farsi pairs and context"
        )
        
        crew = Crew(
            agents=[self.terminology_specialist],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return json.loads(str(result))
    
    def translate_chunk(self, chunk: str, terminology: List[Dict[str, str]]) -> str:
        """Translate a text chunk using specialized agents"""
        
        # Create terminology context
        term_context = "\n".join([f"{term['english']} → {term['farsi']}" for term in terminology])
        
        # Primary translation task
        translation_task = Task(
            description=f"""
            Translate the following English text to Farsi:
            
            Text: {chunk}
            
            Terminology to use:
            {term_context}
            
            Requirements:
            - Maintain academic tone
            - Use provided terminology consistently
            - Preserve original meaning
            - Ensure Farsi fluency
            """,
            agent=self.primary_translator,
            expected_output="High-quality Farsi translation"
        )
        
        # Quality review task
        review_task = Task(
            description=f"""
            Review and improve the Farsi translation for:
            - Accuracy
            - Fluency
            - Terminology consistency
            - Academic tone
            
            Original text: {chunk}
            Translation to review: [Previous agent's output]
            """,
            agent=self.quality_reviewer,
            expected_output="Improved Farsi translation with quality notes"
        )
        
        crew = Crew(
            agents=[self.primary_translator, self.quality_reviewer],
            tasks=[translation_task, review_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return str(result)
    
    def process_chapter(self, chapter_text: str, chapter_number: int, document_id: int) -> Dict[str, Any]:
        """Process a complete chapter through the translation pipeline"""
        
        print(f"🔄 Processing Chapter {chapter_number}")
        
        # 1. Analyze content
        print("📊 Analyzing content...")
        analysis = self.analyze_content(chapter_text)
        
        # 2. Extract terminology
        print("🔤 Extracting terminology...")
        terminology = self.extract_terminology(chapter_text)
        
        # 3. Chunk text
        print("✂️  Chunking text...")
        chunks = self.text_splitter.split_text(chapter_text)
        
        # 4. Save chapter to database
        chapter_file = f"chapters/chapter_{chapter_number:03d}_original.txt"
        os.makedirs("chapters", exist_ok=True)
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        
        chapter_id = save_chapter(
            document_id=document_id,
            chapter_number=chapter_number,
            title=f"Chapter {chapter_number}",
            start_page=1,  # Will be updated based on actual pages
            end_page=len(chunks),
            original_text=chapter_text,
            file_path=chapter_file
        )
        
        # 5. Process each chunk
        translated_chunks = []
        farsi_file_path = f"chapters/chapter_{chapter_number:03d}_farsi.txt"
        
        with open(farsi_file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== CHAPTER {chapter_number} - FARSI TRANSLATION ===\n\n")
            
            for i, chunk in enumerate(chunks):
                print(f"🔄 Translating chunk {i+1}/{len(chunks)}")
                
                # Save chunk to database
                chunk_id = save_text_chunk(
                    chapter_id=chapter_id,
                    chunk_number=i+1,
                    original_text=chunk,
                    chunk_size=len(chunk),
                    token_count=len(self.tokenizer.encode(chunk)),
                    page_references=[i+1]  # Simplified for now
                )
                
                # Translate chunk
                translated_chunk = self.translate_chunk(chunk, terminology)
                translated_chunks.append(translated_chunk)
                
                # Save translation job
                save_translation_job(
                    chapter_id=chapter_id,
                    chunk_id=chunk_id,
                    agent_name="Multi-Agent Pipeline",
                    agent_role="Primary Translator + Quality Reviewer",
                    original_text=chunk,
                    translated_text=translated_chunk,
                    model_used="gpt-4o",
                    confidence_score=0.9  # High confidence for multi-agent approach
                )
                
                # Write to file
                f.write(f"--- Chunk {i+1} ---\n")
                f.write(translated_chunk)
                f.write("\n\n")
        
        # 6. Consistency check
        print("🔍 Checking consistency...")
        consistency_task = Task(
            description=f"""
            Review all translations for consistency:
            {chr(10).join(translated_chunks[:3])}...
            
            Check for:
            - Terminology consistency
            - Style consistency
            - Tone consistency
            """,
            agent=self.consistency_checker,
            expected_output="Consistency report and recommendations"
        )
        
        crew = Crew(
            agents=[self.consistency_checker],
            tasks=[consistency_task],
            verbose=True,
            process=Process.sequential
        )
        
        consistency_result = crew.kickoff()
        
        print(f"✅ Chapter {chapter_number} processed successfully!")
        
        return {
            "chapter_id": chapter_id,
            "chunks_processed": len(chunks),
            "terminology_extracted": len(terminology),
            "farsi_file": farsi_file_path,
            "consistency_report": str(consistency_result)
        }
    
    def process_document(self, document_id: int, chapters: List[str]):
        """Process entire document through translation pipeline"""
        
        print(f"🚀 Starting multi-agent translation pipeline for document {document_id}")
        print(f"📊 Processing {len(chapters)} chapters")
        
        results = []
        
        for i, chapter_text in enumerate(chapters, 1):
            try:
                result = self.process_chapter(chapter_text, i, document_id)
                results.append(result)
                
                print(f"📈 Progress: {i}/{len(chapters)} chapters completed")
                
            except Exception as e:
                print(f"❌ Error processing chapter {i}: {str(e)}")
                continue
        
        print(f"🎉 Document processing completed!")
        print(f"📊 Results: {len(results)} chapters processed successfully")
        
        return results

def main():
    """Main function to run the translation pipeline"""
    
    # Initialize pipeline
    pipeline = MultiAgentTranslationPipeline()
    
    # Example usage - process sample chapters
    sample_chapters = [
        "This is chapter 1 content...",
        "This is chapter 2 content...",
        # Add more chapters as needed
    ]
    
    # Process document
    results = pipeline.process_document(document_id=1, chapters=sample_chapters)
    
    print("🎉 Translation pipeline completed!")
    for result in results:
        print(f"Chapter {result['chapter_id']}: {result['chunks_processed']} chunks processed")

if __name__ == "__main__":
    main()
