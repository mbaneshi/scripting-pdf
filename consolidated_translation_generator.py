#!/usr/bin/env python3
"""
Consolidated Translation File Generator
Creates a single MD file with 200 pages for large chat translation
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path

def create_consolidated_translation_file(pages_dir: str = "simple_pages", output_file: str = "consolidated_200_pages.md", max_pages: int = 200):
    """Create a single MD file with 200 pages for large chat translation"""
    
    print(f"📝 Creating consolidated translation file with {max_pages} pages...")
    
    # Get page files
    page_files = sorted([f for f in os.listdir(pages_dir) if f.startswith("page_") and f.endswith(".txt")])
    
    if not page_files:
        print("❌ No page files found")
        return
    
    # Limit to max_pages
    page_files = page_files[:max_pages]
    
    print(f"📄 Processing {len(page_files)} pages")
    
    # Create terminology database
    terminology_db = create_terminology_database()
    
    # Start building consolidated content
    consolidated_content = f"""# Consolidated Translation - Pages 1-{max_pages}

## 📋 Translation Instructions

### Context
- **Source**: "Speaking Being: Werner Erhard, Martin Heidegger, and a New Possibility of Being Human"
- **Authors**: Bruce Hyde and Drew Kopp
- **Pages**: 1-{max_pages}
- **Content Type**: Mixed dialogue + Academic exposition
- **Total Pages**: {len(page_files)}

### 🎯 Translation Requirements

1. **Maintain Academic Tone**: This is philosophical content requiring precision
2. **Handle Dialogue**: ERHARD speaks formally, participants speak conversationally
3. **Preserve Citations**: Keep citations like (BT 185), (FCM 4) exactly
4. **Use Terminology**: Apply the terminology database consistently
5. **Natural Farsi**: Ensure fluent, readable Farsi expression
6. **Page Structure**: Maintain page breaks and numbering

### 🔤 Terminology Database

Use these terms consistently throughout all {max_pages} pages:

#### Heidegger Terms
"""
    
    # Add terminology section
    heidegger_terms = {k: v for k, v in terminology_db.items() if k in ["Dasein", "Being", "authenticity", "inauthenticity", "thrownness", "projection", "temporality", "historicity", "ontological", "ontic", "presence", "absence", "disclosure", "concealment", "truth", "unconcealment", "aletheia", "care", "anxiety", "death"]}
    for eng, farsi in heidegger_terms.items():
        consolidated_content += f"- {eng} → {farsi}\n"
    
    consolidated_content += "\n#### Erhard Terms\n"
    erhard_terms = {k: v for k, v in terminology_db.items() if k in ["racket", "story", "what happened", "declaration", "assertion", "responsibility", "guilt", "empowerment", "transformation", "possibility", "being", "occurring", "correlate", "distinction"]}
    for eng, farsi in erhard_terms.items():
        consolidated_content += f"- {eng} → {farsi}\n"
    
    consolidated_content += "\n#### Academic Terms\n"
    academic_terms = {k: v for k, v in terminology_db.items() if k in ["ontology", "epistemology", "phenomenology", "hermeneutics", "metaphysics", "consciousness", "self-consciousness", "reflexion", "paradigm", "Cartesian", "rhetoric", "evocation", "authentic", "inauthentic", "existential", "existentialism"]}
    for eng, farsi in academic_terms.items():
        consolidated_content += f"- {eng} → {farsi}\n"
    
    consolidated_content += f"""

### 🤖 Translation Prompt

Please translate the following {max_pages} pages to Farsi following these guidelines:

1. **Context**: This is from a philosophical book about Werner Erhard and Martin Heidegger
2. **Tone**: Maintain academic precision while ensuring natural Farsi expression
3. **Dialogue**: If you see dialogue (ERHARD:, HANNAH:, etc.), maintain speaker distinctions
4. **Citations**: Preserve all citations exactly (e.g., (BT 185), (FCM 4))
5. **Terminology**: Use the terminology database above consistently
6. **Structure**: Maintain page breaks and numbering
7. **Format**: Provide translation in the same format as the original

### 📝 Original Text ({max_pages} Pages)

"""
    
    # Process each page
    total_chars = 0
    for i, page_file in enumerate(page_files, 1):
        page_num = int(page_file.split('_')[1].split('.')[0])
        
        print(f"🔄 Processing page {page_num} ({i}/{len(page_files)})")
        
        # Read page content
        page_path = os.path.join(pages_dir, page_file)
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                page_content = f.read()
        except Exception as e:
            print(f"❌ Error reading {page_file}: {str(e)}")
            continue
        
        # Clean page content
        clean_content = page_content.replace("=== PAGE", "## PAGE").replace("=== END OF PAGE", "## END OF PAGE")
        
        # Add page to consolidated content
        consolidated_content += f"\n---\n\n## PAGE {page_num}\n\n"
        consolidated_content += clean_content
        consolidated_content += f"\n\n## END OF PAGE {page_num}\n\n"
        
        total_chars += len(page_content)
        
        if i % 50 == 0:
            print(f"📊 Processed {i} pages, {total_chars:,} characters so far")
    
    # Add final sections
    consolidated_content += f"""

---

## 📄 Your Translation

[Please provide your Farsi translation here, maintaining the same page structure]

---

## 📊 Translation Quality Checklist

- [ ] Academic tone maintained throughout all {max_pages} pages
- [ ] Terminology used consistently across all pages
- [ ] Citations preserved exactly
- [ ] Dialogue handled appropriately
- [ ] Natural Farsi expression
- [ ] Page structure maintained
- [ ] Philosophical meaning preserved
- [ ] Consistent terminology across all {max_pages} pages

## 📝 Notes

[Add any translation notes or challenges here]

---

**File**: {output_file}
**Created**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Pages**: 1-{max_pages}
**Total Characters**: {total_chars:,}
**Total Words**: {total_chars // 5:,} (estimated)
"""
    
    # Write consolidated file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_content)
    
    print(f"✅ Created consolidated file: {output_file}")
    print(f"📊 Total characters: {total_chars:,}")
    print(f"📊 Total words (estimated): {total_chars // 5:,}")
    print(f"📄 Pages included: {len(page_files)}")
    
    return total_chars, len(page_files)

def create_terminology_database() -> Dict[str, str]:
    """Create terminology database for consistent translation"""
    
    return {
        # Heidegger Terms
        "Dasein": "دازاین",
        "Being": "هستی",
        "authenticity": "اصالت",
        "inauthenticity": "عدم اصالت",
        "thrownness": "پرتاب شدگی",
        "projection": "طرح ریزی",
        "temporality": "زمانمندی",
        "historicity": "تاریخیت",
        "ontological": "هستیشناختی",
        "ontic": "هستی",
        "presence": "حضور",
        "absence": "غیاب",
        "disclosure": "افشا",
        "concealment": "پنهان سازی",
        "truth": "حقیقت",
        "unconcealment": "عدم پنهان سازی",
        "aletheia": "آلتیا",
        "care": "مراقبت",
        "anxiety": "اضطراب",
        "death": "مرگ",
        
        # Erhard Terms
        "racket": "راکت",
        "story": "داستان",
        "what happened": "آنچه اتفاق افتاد",
        "declaration": "اعلام",
        "assertion": "ادعا",
        "responsibility": "مسئولیت",
        "guilt": "گناه",
        "empowerment": "توانمندسازی",
        "transformation": "تحول",
        "possibility": "امکان",
        "being": "بودن",
        "occurring": "رخ دادن",
        "correlate": "همبسته",
        "distinction": "تمایز",
        
        # Academic Terms
        "ontology": "هستیشناسی",
        "epistemology": "شناختشناسی",
        "phenomenology": "پدیدارشناسی",
        "hermeneutics": "هرمنوتیک",
        "metaphysics": "متافیزیک",
        "consciousness": "آگاهی",
        "self-consciousness": "خودآگاهی",
        "reflexion": "بازتاب",
        "paradigm": "الگو",
        "Cartesian": "دکارتی",
        "rhetoric": "بلاغت",
        "evocation": "فراخوانی",
        "authentic": "اصیل",
        "inauthentic": "غیراصیل",
        "existential": "وجودی",
        "existentialism": "وجودگرایی"
    }

def check_chat_limits():
    """Check character limits for different chat services"""
    
    limits = {
        "ChatGPT-4": "128,000 tokens (~500,000 characters)",
        "ChatGPT-4o": "128,000 tokens (~500,000 characters)",
        "Claude-3.5-Sonnet": "200,000 tokens (~800,000 characters)",
        "Claude-3-Opus": "200,000 tokens (~800,000 characters)",
        "Gemini Pro": "1,000,000 tokens (~4,000,000 characters)",
        "Gemini Ultra": "1,000,000 tokens (~4,000,000 characters)"
    }
    
    print("📊 Chat Service Character Limits:")
    print("-" * 50)
    for service, limit in limits.items():
        print(f"{service}: {limit}")
    print("-" * 50)

def main():
    """Main function"""
    
    print("🚀 Creating Consolidated Translation File")
    print("=" * 60)
    
    # Check chat limits
    check_chat_limits()
    
    # Create consolidated file
    total_chars, total_pages = create_consolidated_translation_file(
        pages_dir="simple_pages",
        output_file="consolidated_200_pages.md",
        max_pages=200
    )
    
    print(f"\n🎉 Consolidated translation file ready!")
    print(f"📊 File: consolidated_200_pages.md")
    print(f"📄 Pages: {total_pages}")
    print(f"📊 Characters: {total_chars:,}")
    print(f"📊 Words (estimated): {total_chars // 5:,}")
    
    # Check if it fits in different chat services
    print(f"\n📊 Chat Service Compatibility:")
    if total_chars < 500000:
        print("✅ Fits in ChatGPT-4/4o")
    if total_chars < 800000:
        print("✅ Fits in Claude-3.5-Sonnet/3-Opus")
    if total_chars < 4000000:
        print("✅ Fits in Gemini Pro/Ultra")
    
    print(f"\n🚀 Usage:")
    print(f"1. Open consolidated_200_pages.md")
    print(f"2. Copy entire content")
    print(f"3. Paste into chat")
    print(f"4. Ask: 'Please translate this to Farsi'")
    print(f"5. Copy Farsi translation back")

if __name__ == "__main__":
    main()
