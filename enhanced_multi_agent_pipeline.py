#!/usr/bin/env python3
"""
Enhanced Multi-Agent Translation Pipeline with Precise Prompts
Uses content analysis to create specialized prompts for each agent
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
from precise_prompt_designer import ContentAnalyzer, PrecisePromptDesigner

class EnhancedMultiAgentPipeline:
    def __init__(self, openai_api_key: str = None):
        """Initialize the enhanced multi-agent translation pipeline"""
        
        print("🚀 Initializing Enhanced Multi-Agent Translation Pipeline")
        
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
        
        # Content analyzer for prompt generation
        self.content_analyzer = ContentAnalyzer()
        
        # Initialize database
        create_tables()
        
        print("✅ Enhanced pipeline initialized successfully")
    
    def analyze_content_for_prompts(self, text: str) -> Dict[str, str]:
        """Analyze content and generate specialized prompts"""
        
        print("🔍 Analyzing content for precise prompt generation...")
        
        # Analyze content characteristics
        analysis = self.content_analyzer.analyze_content_characteristics([text])
        
        # Create specialized prompts
        prompt_designer = PrecisePromptDesigner(analysis)
        prompts = prompt_designer.create_specialized_prompts()
        
        print(f"✅ Generated {len(prompts)} specialized prompts")
        
        return prompts
    
    def create_enhanced_agents(self, prompts: Dict[str, str]):
        """Create agents with specialized prompts"""
        
        print("🤖 Creating enhanced agents with specialized prompts...")
        
        # 1. Content Analyzer Agent
        self.content_analyzer_agent = Agent(
            role="Content Analysis Expert",
            goal="Analyze philosophical and academic texts with precision",
            backstory="""You are an expert content analyst specializing in philosophical and academic texts. 
            You excel at identifying text structure, themes, terminology, and translation complexity.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 2. Terminology Specialist Agent
        self.terminology_specialist_agent = Agent(
            role="Terminology Specialist",
            goal="Ensure consistent and accurate translation of specialized philosophical terms",
            backstory="""You are a terminology expert specializing in Heideggerian and Erhardian philosophy. 
            You maintain consistency in philosophical terms and ensure accurate academic translation.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 3. Primary Translator Agent
        self.primary_translator_agent = Agent(
            role="Professional Academic Translator",
            goal="Translate English to Farsi with highest accuracy and academic precision",
            backstory="""You are a professional translator specializing in academic and philosophical texts. 
            You translate with precision while maintaining the original meaning and academic tone.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 4. Quality Reviewer Agent
        self.quality_reviewer_agent = Agent(
            role="Quality Review Expert",
            goal="Ensure highest quality and accuracy in Farsi translations",
            backstory="""You are a quality assurance expert specializing in Farsi translations. 
            You ensure translations are accurate, fluent, and consistent with established terminology.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 5. Consistency Checker Agent
        self.consistency_checker_agent = Agent(
            role="Consistency Expert",
            goal="Ensure uniform terminology and style across all translations",
            backstory="""You are a consistency expert who ensures all translations maintain uniform terminology 
            and style throughout the document. You catch inconsistencies and suggest improvements.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        print("✅ Enhanced agents created successfully")
    
    def analyze_content_with_precise_prompt(self, text: str, prompts: Dict[str, str]) -> Dict[str, Any]:
        """Analyze content using precise prompt"""
        
        prompt = prompts["content_analyzer"].format(text=text[:1000] + "...")
        
        task = Task(
            description=prompt,
            agent=self.content_analyzer_agent,
            expected_output="JSON analysis with structure, themes, terminology, complexity_assessment, and recommendations"
        )
        
        crew = Crew(
            agents=[self.content_analyzer_agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except json.JSONDecodeError:
            return {"analysis": str(result), "structure": "mixed", "complexity": "high"}
    
    def extract_terminology_with_precise_prompt(self, text: str, prompts: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract terminology using precise prompt"""
        
        prompt = prompts["terminology_specialist"].format(text=text[:1500] + "...")
        
        task = Task(
            description=prompt,
            agent=self.terminology_specialist_agent,
            expected_output="List of terminology with English-Farsi pairs and context"
        )
        
        crew = Crew(
            agents=[self.terminology_specialist_agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        
        try:
            return json.loads(str(result))
        except json.JSONDecodeError:
            # Fallback to simple extraction
            return [{"english": "term", "farsi": "ترجمه", "context": "explanation", "category": "general"}]
    
    def translate_chunk_with_precise_prompt(self, chunk: str, terminology: List[Dict[str, str]], prompts: Dict[str, str]) -> str:
        """Translate chunk using precise prompt"""
        
        # Format terminology for prompt
        term_context = "\n".join([f"{term['english']} → {term['farsi']}" for term in terminology])
        
        prompt = prompts["primary_translator"].format(
            text=chunk,
            terminology=term_context
        )
        
        # Primary translation task
        translation_task = Task(
            description=prompt,
            agent=self.primary_translator_agent,
            expected_output="High-quality Farsi translation"
        )
        
        # Quality review task
        review_prompt = prompts["quality_reviewer"].format(
            original_text=chunk,
            translation="[Previous agent's output]",
            terminology=term_context
        )
        
        review_task = Task(
            description=review_prompt,
            agent=self.quality_reviewer_agent,
            expected_output="Improved Farsi translation with quality notes"
        )
        
        crew = Crew(
            agents=[self.primary_translator_agent, self.quality_reviewer_agent],
            tasks=[translation_task, review_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return str(result)
    
    def process_chapter_with_precise_prompts(self, chapter_text: str, chapter_number: int, document_id: int) -> Dict[str, Any]:
        """Process chapter using precise prompts"""
        
        print(f"🔄 Processing Chapter {chapter_number} with precise prompts")
        
        # 1. Generate specialized prompts based on content
        prompts = self.analyze_content_for_prompts(chapter_text)
        
        # 2. Create enhanced agents
        self.create_enhanced_agents(prompts)
        
        # 3. Analyze content with precise prompt
        print("📊 Analyzing content with precise prompt...")
        analysis = self.analyze_content_with_precise_prompt(chapter_text, prompts)
        
        # 4. Extract terminology with precise prompt
        print("🔤 Extracting terminology with precise prompt...")
        terminology = self.extract_terminology_with_precise_prompt(chapter_text, prompts)
        
        # 5. Chunk text
        print("✂️  Chunking text...")
        chunks = self.text_splitter.split_text(chapter_text)
        
        # 6. Save chapter to database
        chapter_file = f"chapters/chapter_{chapter_number:03d}_original.txt"
        os.makedirs("chapters", exist_ok=True)
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        
        chapter_id = save_chapter(
            document_id=document_id,
            chapter_number=chapter_number,
            title=f"Chapter {chapter_number}",
            start_page=1,
            end_page=len(chunks),
            original_text=chapter_text,
            file_path=chapter_file
        )
        
        # 7. Process each chunk with precise prompts
        translated_chunks = []
        farsi_file_path = f"chapters/chapter_{chapter_number:03d}_farsi.txt"
        
        with open(farsi_file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== CHAPTER {chapter_number} - FARSI TRANSLATION ===\n\n")
            
            for i, chunk in enumerate(chunks):
                print(f"🔄 Translating chunk {i+1}/{len(chunks)} with precise prompts")
                
                # Save chunk to database
                chunk_id = save_text_chunk(
                    chapter_id=chapter_id,
                    chunk_number=i+1,
                    original_text=chunk,
                    chunk_size=len(chunk),
                    token_count=len(self.tokenizer.encode(chunk)),
                    page_references=[i+1]
                )
                
                # Translate chunk with precise prompt
                translated_chunk = self.translate_chunk_with_precise_prompt(chunk, terminology, prompts)
                translated_chunks.append(translated_chunk)
                
                # Save translation job
                save_translation_job(
                    chapter_id=chapter_id,
                    chunk_id=chunk_id,
                    agent_name="Enhanced Multi-Agent Pipeline",
                    agent_role="Precise Prompt Translation",
                    original_text=chunk,
                    translated_text=translated_chunk,
                    model_used="gpt-4o",
                    confidence_score=0.95  # Higher confidence with precise prompts
                )
                
                # Write to file
                f.write(f"--- Chunk {i+1} ---\n")
                f.write(translated_chunk)
                f.write("\n\n")
        
        # 8. Consistency check with precise prompt
        print("🔍 Checking consistency with precise prompt...")
        consistency_prompt = prompts["consistency_checker"].format(
            translations="\n".join(translated_chunks[:3]),
            terminology="\n".join([f"{term['english']} → {term['farsi']}" for term in terminology])
        )
        
        consistency_task = Task(
            description=consistency_prompt,
            agent=self.consistency_checker_agent,
            expected_output="Consistency report and recommendations"
        )
        
        crew = Crew(
            agents=[self.consistency_checker_agent],
            tasks=[consistency_task],
            verbose=True,
            process=Process.sequential
        )
        
        consistency_result = crew.kickoff()
        
        print(f"✅ Chapter {chapter_number} processed with precise prompts!")
        
        return {
            "chapter_id": chapter_id,
            "chunks_processed": len(chunks),
            "terminology_extracted": len(terminology),
            "farsi_file": farsi_file_path,
            "consistency_report": str(consistency_result),
            "prompts_used": len(prompts),
            "analysis": analysis
        }
    
    def process_document_with_precise_prompts(self, document_id: int, chapters: List[str]):
        """Process entire document with precise prompts"""
        
        print(f"🚀 Starting enhanced multi-agent translation with precise prompts")
        print(f"📊 Processing {len(chapters)} chapters")
        
        results = []
        
        for i, chapter_text in enumerate(chapters, 1):
            try:
                result = self.process_chapter_with_precise_prompts(chapter_text, i, document_id)
                results.append(result)
                
                print(f"📈 Progress: {i}/{len(chapters)} chapters completed")
                
            except Exception as e:
                print(f"❌ Error processing chapter {i}: {str(e)}")
                continue
        
        print(f"🎉 Document processing with precise prompts completed!")
        print(f"📊 Results: {len(results)} chapters processed successfully")
        
        return results

def main():
    """Main function to run the enhanced translation pipeline"""
    
    # Initialize enhanced pipeline
    pipeline = EnhancedMultiAgentPipeline()
    
    # Example usage - process sample chapters
    sample_chapters = [
        "This is chapter 1 content...",
        "This is chapter 2 content...",
        # Add more chapters as needed
    ]
    
    # Process document with precise prompts
    results = pipeline.process_document_with_precise_prompts(document_id=1, chapters=sample_chapters)
    
    print("🎉 Enhanced translation pipeline completed!")
    for result in results:
        print(f"Chapter {result['chapter_id']}: {result['chunks_processed']} chunks processed")

if __name__ == "__main__":
    main()
