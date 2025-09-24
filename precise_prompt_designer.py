#!/usr/bin/env python3
"""
Precise Prompt Designer for Multi-Agent Translation
Analyzes content characteristics and creates specialized prompts
"""

import re
from typing import Dict, List, Any
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        self.content_samples = []
        self.terminology_patterns = []
        self.dialogue_patterns = []
        self.academic_patterns = []
    
    def analyze_content_characteristics(self, pages: List[str]) -> Dict[str, Any]:
        """Analyze content to identify key characteristics for prompt design"""
        
        print("🔍 Analyzing content characteristics...")
        
        # Combine all content
        full_text = "\n".join(pages)
        
        # 1. Identify text types and patterns
        text_types = self._identify_text_types(full_text)
        
        # 2. Extract philosophical terminology
        terminology = self._extract_terminology(full_text)
        
        # 3. Identify dialogue patterns
        dialogue_patterns = self._analyze_dialogue(full_text)
        
        # 4. Analyze academic writing style
        academic_style = self._analyze_academic_style(full_text)
        
        # 5. Identify Heidegger/Erhard specific concepts
        philosophical_concepts = self._extract_philosophical_concepts(full_text)
        
        return {
            "text_types": text_types,
            "terminology": terminology,
            "dialogue_patterns": dialogue_patterns,
            "academic_style": academic_style,
            "philosophical_concepts": philosophical_concepts,
            "content_length": len(full_text),
            "word_count": len(full_text.split())
        }
    
    def _identify_text_types(self, text: str) -> Dict[str, Any]:
        """Identify different types of content"""
        
        # Dialogue patterns (ERHARD:, HANNAH:, etc.)
        dialogue_lines = re.findall(r'^[A-Z]+\s*:', text, re.MULTILINE)
        
        # Academic citations (Heidegger, Erhard, etc.)
        citations = re.findall(r'\([A-Z]{2,3}\s+\d+\)', text)
        
        # Philosophical terms in quotes
        quoted_terms = re.findall(r'"([^"]+)"', text)
        
        # Page numbers and headers
        page_headers = re.findall(r'^\d+\s*$', text, re.MULTILINE)
        
        return {
            "dialogue_speakers": list(set(dialogue_lines)),
            "citation_count": len(citations),
            "quoted_terms": quoted_terms[:20],  # First 20
            "page_headers": len(page_headers),
            "has_dialogue": len(dialogue_lines) > 0,
            "has_citations": len(citations) > 0
        }
    
    def _extract_terminology(self, text: str) -> Dict[str, List[str]]:
        """Extract specialized terminology"""
        
        # Heidegger-specific terms
        heidegger_terms = [
            "Dasein", "Being", "authenticity", "inauthenticity", "thrownness",
            "projection", "temporality", "historicity", "ontological", "ontic",
            "presence", "absence", "disclosure", "concealment", "truth",
            "unconcealment", "aletheia", "care", "anxiety", "death"
        ]
        
        # Erhard-specific terms
        erhard_terms = [
            "racket", "story", "what happened", "declaration", "assertion",
            "responsibility", "guilt", "empowerment", "transformation",
            "possibility", "being", "occurring", "correlate", "distinction"
        ]
        
        # Academic/philosophical terms
        academic_terms = [
            "ontology", "epistemology", "phenomenology", "hermeneutics",
            "metaphysics", "consciousness", "self-consciousness", "reflexion",
            "paradigm", "Cartesian", "rhetoric", "evocation", "authentic",
            "inauthentic", "existential", "existentialism"
        ]
        
        found_terms = {
            "heidegger": [],
            "erhard": [],
            "academic": []
        }
        
        # Check for term occurrences
        for term in heidegger_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found_terms["heidegger"].append(term)
        
        for term in erhard_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found_terms["erhard"].append(term)
        
        for term in academic_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found_terms["academic"].append(term)
        
        return found_terms
    
    def _analyze_dialogue(self, text: str) -> Dict[str, Any]:
        """Analyze dialogue patterns"""
        
        # Extract dialogue blocks
        dialogue_blocks = re.findall(r'^([A-Z]+)\s*\n(.*?)(?=\n[A-Z]+\s*:|$)', text, re.MULTILINE | re.DOTALL)
        
        speakers = [block[0] for block in dialogue_blocks]
        speaker_counts = Counter(speakers)
        
        return {
            "total_dialogue_blocks": len(dialogue_blocks),
            "unique_speakers": len(speaker_counts),
            "main_speakers": dict(speaker_counts.most_common(5)),
            "dialogue_percentage": len("".join([block[1] for block in dialogue_blocks])) / len(text) * 100
        }
    
    def _analyze_academic_style(self, text: str) -> Dict[str, Any]:
        """Analyze academic writing characteristics"""
        
        # Sentence complexity
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Citation patterns
        citations = re.findall(r'\([A-Z]{2,3}\s+\d+\)', text)
        
        # Academic phrases
        academic_phrases = [
            "it is important to note", "furthermore", "moreover", "however",
            "in other words", "that is to say", "as we have seen", "it follows that"
        ]
        
        found_phrases = [phrase for phrase in academic_phrases if phrase in text.lower()]
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "citation_count": len(citations),
            "academic_phrases": found_phrases,
            "complexity_level": "high" if avg_sentence_length > 20 else "medium"
        }
    
    def _extract_philosophical_concepts(self, text: str) -> Dict[str, List[str]]:
        """Extract key philosophical concepts"""
        
        # Key concepts from the text
        concepts = {
            "being_and_time": ["Dasein", "Being", "temporality", "historicity"],
            "authenticity": ["authentic", "inauthentic", "genuine", "real"],
            "consciousness": ["consciousness", "self-consciousness", "awareness", "reflexion"],
            "language": ["language", "speaking", "communication", "rhetoric"],
            "transformation": ["transformation", "change", "possibility", "empowerment"]
        }
        
        found_concepts = {}
        for category, terms in concepts.items():
            found_terms = [term for term in terms if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE)]
            if found_terms:
                found_concepts[category] = found_terms
        
        return found_concepts

class PrecisePromptDesigner:
    def __init__(self, content_analysis: Dict[str, Any]):
        self.analysis = content_analysis
    
    def create_specialized_prompts(self) -> Dict[str, str]:
        """Create specialized prompts based on content analysis"""
        
        prompts = {}
        
        # 1. Content Analyzer Prompt
        prompts["content_analyzer"] = self._create_content_analyzer_prompt()
        
        # 2. Terminology Specialist Prompt
        prompts["terminology_specialist"] = self._create_terminology_prompt()
        
        # 3. Primary Translator Prompt
        prompts["primary_translator"] = self._create_translator_prompt()
        
        # 4. Quality Reviewer Prompt
        prompts["quality_reviewer"] = self._create_reviewer_prompt()
        
        # 5. Consistency Checker Prompt
        prompts["consistency_checker"] = self._create_consistency_prompt()
        
        return prompts
    
    def _create_content_analyzer_prompt(self) -> str:
        """Create prompt for content analysis agent"""
        
        return f"""
You are a Content Analysis Expert specializing in philosophical and academic texts. Your task is to analyze the following text and provide a comprehensive analysis.

CONTEXT: This text is from "Speaking Being: Werner Erhard, Martin Heidegger, and a New Possibility of Being Human" by Bruce Hyde and Drew Kopp.

CONTENT CHARACTERISTICS IDENTIFIED:
- Text contains dialogue between ERHARD and participants
- Academic citations: {self.analysis['text_types']['citation_count']} citations found
- Philosophical terminology: {len(self.analysis['terminology']['heidegger'])} Heidegger terms, {len(self.analysis['terminology']['erhard'])} Erhard terms
- Dialogue speakers: {', '.join(self.analysis['text_types']['dialogue_speakers'][:5])}
- Academic complexity: {self.analysis['academic_style']['complexity_level']} level

ANALYSIS REQUIREMENTS:
1. Identify text structure (dialogue, narrative, academic exposition)
2. Extract key philosophical concepts and themes
3. Identify specialized terminology that needs consistent translation
4. Assess translation complexity and challenges
5. Recommend chunking strategy for optimal translation

OUTPUT FORMAT: JSON with structure, themes, terminology, complexity_assessment, and recommendations.

TEXT TO ANALYZE:
{{text}}
"""
    
    def _create_terminology_prompt(self) -> str:
        """Create prompt for terminology specialist"""
        
        heidegger_terms = self.analysis['terminology']['heidegger']
        erhard_terms = self.analysis['terminology']['erhard']
        academic_terms = self.analysis['terminology']['academic']
        
        return f"""
You are a Terminology Specialist for philosophical translation. Your expertise is in maintaining consistent translation of specialized terms across Heideggerian and Erhardian philosophy.

ESTABLISHED TERMINOLOGY DATABASE:

HEIDEGGER TERMS (found in text):
{chr(10).join([f"- {term}" for term in heidegger_terms])}

ERHARD TERMS (found in text):
{chr(10).join([f"- {term}" for term in erhard_terms])}

ACADEMIC TERMS (found in text):
{chr(10).join([f"- {term}" for term in academic_terms])}

TRANSLATION GUIDELINES:
1. Maintain consistency with established philosophical terminology
2. Use standard Farsi translations for Heideggerian concepts
3. Preserve Erhard's unique terminology and concepts
4. Ensure academic tone and precision
5. Consider context and philosophical meaning

TASK: Extract all specialized terminology from the text and provide standardized Farsi translations with context explanations.

OUTPUT FORMAT: List of {{"english": "term", "farsi": "ترجمه", "context": "explanation", "category": "heidegger/erhard/academic"}}

TEXT TO ANALYZE:
{{text}}
"""
    
    def _create_translator_prompt(self) -> str:
        """Create prompt for primary translator"""
        
        return f"""
You are a Professional Academic Translator specializing in philosophical texts. You translate English to Farsi with the highest accuracy and academic precision.

TRANSLATION CONTEXT:
- Source: "Speaking Being: Werner Erhard, Martin Heidegger, and a New Possibility of Being Human"
- Authors: Bruce Hyde and Drew Kopp
- Content: Philosophical dialogue and academic exposition
- Target audience: Farsi-speaking academics and philosophers

TRANSLATION REQUIREMENTS:
1. Maintain academic tone and precision
2. Preserve philosophical meaning and nuance
3. Use established terminology consistently
4. Ensure natural Farsi expression
5. Handle dialogue with appropriate conversational tone
6. Preserve citations and references exactly
7. Maintain paragraph structure and formatting

DIALOGUE HANDLING:
- ERHARD: Use formal, philosophical tone
- Participants: Use natural conversational tone
- Preserve speaker names exactly

CITATION HANDLING:
- Preserve all citations exactly: (BT 185), (FCM 4), etc.
- Maintain academic reference format

OUTPUT: High-quality Farsi translation that maintains academic integrity while being natural and readable.

TEXT TO TRANSLATE:
{{text}}

TERMINOLOGY TO USE:
{{terminology}}
"""
    
    def _create_reviewer_prompt(self) -> str:
        """Create prompt for quality reviewer"""
        
        return f"""
You are a Quality Review Expert for Farsi translations of philosophical texts. Your role is to ensure the highest quality and accuracy.

REVIEW CRITERIA:
1. ACCURACY: Does the translation capture the original meaning?
2. TERMINOLOGY: Is specialized terminology used consistently?
3. FLUENCY: Is the Farsi natural and readable?
4. ACADEMIC TONE: Is the academic style maintained?
5. CONTEXT: Are philosophical concepts properly conveyed?

QUALITY STANDARDS:
- Philosophical precision
- Academic formality
- Natural Farsi expression
- Consistent terminology
- Proper dialogue handling

REVIEW PROCESS:
1. Compare original and translation
2. Check terminology consistency
3. Assess fluency and naturalness
4. Verify academic tone
5. Ensure philosophical accuracy

OUTPUT: Improved translation with quality notes explaining changes made.

ORIGINAL TEXT:
{{original_text}}

TRANSLATION TO REVIEW:
{{translation}}

TERMINOLOGY DATABASE:
{{terminology}}
"""
    
    def _create_consistency_prompt(self) -> str:
        """Create prompt for consistency checker"""
        
        return f"""
You are a Consistency Expert ensuring uniform terminology and style across all translations in this philosophical work.

CONSISTENCY REQUIREMENTS:
1. TERMINOLOGY: Same English terms must always translate to same Farsi terms
2. STYLE: Uniform academic tone throughout
3. FORMATTING: Consistent handling of citations, dialogue, and structure
4. PHILOSOPHICAL CONCEPTS: Consistent treatment of Heideggerian and Erhardian concepts

TERMINOLOGY CONSISTENCY CHECKLIST:
- Heidegger terms: Dasein, Being, authenticity, etc.
- Erhard terms: racket, story, responsibility, etc.
- Academic terms: ontology, phenomenology, etc.
- Dialogue formatting: Speaker names and formatting
- Citation format: (BT 185), (FCM 4), etc.

TASK: Review translations for consistency and provide recommendations for standardization.

OUTPUT: Consistency report with specific recommendations for maintaining uniformity.

TRANSLATIONS TO CHECK:
{{translations}}

TERMINOLOGY DATABASE:
{{terminology}}
"""

def main():
    """Main function to analyze content and create prompts"""
    
    print("🔍 Analyzing content for precise prompt design...")
    
    # Sample pages for analysis
    sample_pages = [
        "simple_pages/page_001.txt",
        "simple_pages/page_050.txt", 
        "simple_pages/page_100.txt",
        "simple_pages/page_200.txt",
        "simple_pages/page_300.txt"
    ]
    
    # Read sample pages
    pages_content = []
    for page_file in sample_pages:
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
                pages_content.append(content)
        except FileNotFoundError:
            print(f"⚠️  {page_file} not found, skipping...")
    
    if not pages_content:
        print("❌ No sample pages found for analysis")
        return
    
    # Analyze content
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze_content_characteristics(pages_content)
    
    # Create prompts
    prompt_designer = PrecisePromptDesigner(analysis)
    prompts = prompt_designer.create_specialized_prompts()
    
    # Save prompts
    with open("specialized_prompts.txt", 'w', encoding='utf-8') as f:
        f.write("🎯 SPECIALIZED PROMPTS FOR MULTI-AGENT TRANSLATION\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("📊 CONTENT ANALYSIS SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total content analyzed: {analysis['content_length']} characters\n")
        f.write(f"Word count: {analysis['word_count']} words\n")
        f.write(f"Dialogue speakers: {len(analysis['text_types']['dialogue_speakers'])}\n")
        f.write(f"Citations found: {analysis['text_types']['citation_count']}\n")
        f.write(f"Heidegger terms: {len(analysis['terminology']['heidegger'])}\n")
        f.write(f"Erhard terms: {len(analysis['terminology']['erhard'])}\n")
        f.write(f"Academic terms: {len(analysis['terminology']['academic'])}\n\n")
        
        f.write("🤖 SPECIALIZED PROMPTS\n")
        f.write("-" * 30 + "\n\n")
        
        for agent_name, prompt in prompts.items():
            f.write(f"=== {agent_name.upper().replace('_', ' ')} ===\n\n")
            f.write(prompt)
            f.write("\n\n" + "=" * 60 + "\n\n")
    
    print("✅ Specialized prompts created!")
    print("📄 Saved to: specialized_prompts.txt")
    
    # Print summary
    print("\n📊 CONTENT ANALYSIS SUMMARY:")
    print(f"   Content length: {analysis['content_length']:,} characters")
    print(f"   Word count: {analysis['word_count']:,} words")
    print(f"   Dialogue speakers: {len(analysis['text_types']['dialogue_speakers'])}")
    print(f"   Citations: {analysis['text_types']['citation_count']}")
    print(f"   Heidegger terms: {len(analysis['terminology']['heidegger'])}")
    print(f"   Erhard terms: {len(analysis['terminology']['erhard'])}")
    print(f"   Academic terms: {len(analysis['terminology']['academic'])}")
    
    print("\n🎯 KEY FINDINGS FOR PROMPT DESIGN:")
    print("   1. Mixed content: Dialogue + Academic exposition")
    print("   2. Heavy philosophical terminology")
    print("   3. Multiple speakers in dialogue")
    print("   4. Academic citations throughout")
    print("   5. Complex sentence structures")
    
    return prompts

if __name__ == "__main__":
    prompts = main()
