#!/usr/bin/env python3
"""
Manual Translation Workflow Generator
Creates MD files with prompts and content for manual translation
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path

def create_manual_translation_files(pages_dir: str = "simple_pages", output_dir: str = "manual_translation", max_pages: int = 100):
    """Create MD files for manual translation workflow"""
    
    print(f"📝 Creating manual translation files for {max_pages} pages...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    # Process each page
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
        
        # Create manual translation file
        create_manual_translation_file(page_num, page_content, terminology_db, output_dir)
    
    print(f"✅ Created {len(page_files)} manual translation files in {output_dir}/")
    
    # Create workflow instructions
    create_workflow_instructions(output_dir, len(page_files))
    
    return len(page_files)

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

def create_manual_translation_file(page_num: int, page_content: str, terminology_db: Dict[str, str], output_dir: str):
    """Create MD file for manual translation"""
    
    # Clean page content
    clean_content = page_content.replace("=== PAGE", "## PAGE").replace("=== END OF PAGE", "## END OF PAGE")
    
    # Create filename
    filename = f"page_{page_num:03d}_translation.md"
    filepath = os.path.join(output_dir, filename)
    
    # Create MD content
    md_content = f"""# Manual Translation - Page {page_num}

## 📋 Translation Instructions

### Context
- **Source**: "Speaking Being: Werner Erhard, Martin Heidegger, and a New Possibility of Being Human"
- **Authors**: Bruce Hyde and Drew Kopp
- **Page**: {page_num}
- **Content Type**: Mixed dialogue + Academic exposition

### 🎯 Translation Requirements

1. **Maintain Academic Tone**: This is philosophical content requiring precision
2. **Handle Dialogue**: ERHARD speaks formally, participants speak conversationally
3. **Preserve Citations**: Keep citations like (BT 185), (FCM 4) exactly
4. **Use Terminology**: Apply the terminology database consistently
5. **Natural Farsi**: Ensure fluent, readable Farsi expression

### 🔤 Terminology Database

Use these terms consistently throughout:

"""
    
    # Add terminology section
    md_content += "#### Heidegger Terms\n"
    heidegger_terms = {k: v for k, v in terminology_db.items() if k in ["Dasein", "Being", "authenticity", "inauthenticity", "thrownness", "projection", "temporality", "historicity", "ontological", "ontic", "presence", "absence", "disclosure", "concealment", "truth", "unconcealment", "aletheia", "care", "anxiety", "death"]}
    for eng, farsi in heidegger_terms.items():
        md_content += f"- {eng} → {farsi}\n"
    
    md_content += "\n#### Erhard Terms\n"
    erhard_terms = {k: v for k, v in terminology_db.items() if k in ["racket", "story", "what happened", "declaration", "assertion", "responsibility", "guilt", "empowerment", "transformation", "possibility", "being", "occurring", "correlate", "distinction"]}
    for eng, farsi in erhard_terms.items():
        md_content += f"- {eng} → {farsi}\n"
    
    md_content += "\n#### Academic Terms\n"
    academic_terms = {k: v for k, v in terminology_db.items() if k in ["ontology", "epistemology", "phenomenology", "hermeneutics", "metaphysics", "consciousness", "self-consciousness", "reflexion", "paradigm", "Cartesian", "rhetoric", "evocation", "authentic", "inauthentic", "existential", "existentialism"]}
    for eng, farsi in academic_terms.items():
        md_content += f"- {eng} → {farsi}\n"
    
    md_content += f"""

### 📝 Original Text

```
{clean_content}
```

### 🤖 Translation Prompt

Please translate the above text to Farsi following these guidelines:

1. **Context**: This is from a philosophical book about Werner Erhard and Martin Heidegger
2. **Tone**: Maintain academic precision while ensuring natural Farsi expression
3. **Dialogue**: If you see dialogue (ERHARD:, HANNAH:, etc.), maintain speaker distinctions
4. **Citations**: Preserve all citations exactly (e.g., (BT 185), (FCM 4))
5. **Terminology**: Use the terminology database above consistently
6. **Structure**: Maintain paragraph structure and formatting

### 📄 Your Translation

[Please provide your Farsi translation here]

---

## 📊 Translation Quality Checklist

- [ ] Academic tone maintained
- [ ] Terminology used consistently
- [ ] Citations preserved exactly
- [ ] Dialogue handled appropriately
- [ ] Natural Farsi expression
- [ ] Paragraph structure maintained
- [ ] Philosophical meaning preserved

## 📝 Notes

[Add any translation notes or challenges here]

---

**File**: {filename}
**Created**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Page**: {page_num}
"""
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Created: {filename}")

def create_workflow_instructions(output_dir: str, total_pages: int):
    """Create workflow instructions"""
    
    instructions_file = os.path.join(output_dir, "WORKFLOW_INSTRUCTIONS.md")
    
    instructions = f"""# Manual Translation Workflow Instructions

## 🎯 Overview

This workflow allows you to translate {total_pages} pages manually using AI assistance through chat interfaces.

## 📋 Process

### Step 1: Prepare Translation Files
- ✅ {total_pages} MD files created in `{output_dir}/`
- ✅ Each file contains: original text, terminology database, translation prompt
- ✅ Files named: `page_001_translation.md`, `page_002_translation.md`, etc.

### Step 2: Translation Process
1. **Open a new chat** (ChatGPT, Claude, etc.)
2. **Copy the content** from `page_XXX_translation.md`
3. **Paste into chat** and ask for translation
4. **Copy the Farsi translation** back to the MD file
5. **Repeat for next page**

### Step 3: Quality Control
- Check terminology consistency
- Verify academic tone
- Ensure citations preserved
- Validate philosophical meaning

## 🔤 Terminology Consistency

**Key Terms to Use Consistently:**
- Dasein → دازاین
- Being → هستی
- authenticity → اصالت
- racket → راکت
- story → داستان
- responsibility → مسئولیت
- consciousness → آگاهی
- ontology → هستیشناسی

## 📊 Progress Tracking

- [ ] Page 001: Translated
- [ ] Page 002: Translated
- [ ] Page 003: Translated
- [ ] ... (continue for all {total_pages} pages)

## 🎯 Quality Standards

1. **Accuracy**: Philosophical meaning preserved
2. **Consistency**: Same terms always translated same way
3. **Fluency**: Natural Farsi expression
4. **Tone**: Appropriate academic formality
5. **Structure**: Paragraph formatting maintained

## 🚀 Benefits of This Approach

- **No API costs**: Use free chat interfaces
- **Quality control**: Manual review of each translation
- **Consistency**: Terminology database ensures uniformity
- **Flexibility**: Can adjust approach per page
- **Learning**: Understand translation challenges

## 📝 Tips for Success

1. **Use the terminology database** consistently
2. **Maintain academic tone** for philosophical content
3. **Handle dialogue** appropriately (formal vs. conversational)
4. **Preserve citations** exactly
5. **Check quality** before moving to next page

## 🔄 Next Steps

1. Start with `page_001_translation.md`
2. Copy content to new chat
3. Get Farsi translation
4. Paste back to MD file
5. Repeat for all {total_pages} pages
6. Compile final Farsi document

---

**Total Pages**: {total_pages}
**Created**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: Ready for manual translation
"""
    
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📋 Created workflow instructions: {instructions_file}")

def main():
    """Main function"""
    
    print("🚀 Starting Manual Translation Workflow Generator")
    print("=" * 60)
    
    # Create manual translation files
    total_pages = create_manual_translation_files(
        pages_dir="simple_pages",
        output_dir="manual_translation",
        max_pages=100
    )
    
    print(f"\n🎉 Manual translation workflow ready!")
    print(f"📊 Created {total_pages} translation files")
    print(f"📁 Files in: manual_translation/")
    print(f"📋 Instructions: manual_translation/WORKFLOW_INSTRUCTIONS.md")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Open manual_translation/page_001_translation.md")
    print(f"2. Copy content to new chat")
    print(f"3. Get Farsi translation")
    print(f"4. Paste back to MD file")
    print(f"5. Repeat for all {total_pages} pages")

if __name__ == "__main__":
    main()
