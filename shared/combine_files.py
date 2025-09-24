#!/usr/bin/env python3
"""
File Combination Script for Scripting PDF Project
Combines English and Farsi TOC sections into unified files

Author: AI Assistant
Date: 2025-01-27
Purpose: Create bilingual combined files from English and Farsi TOC sections
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

class FileCombiner:
    def __init__(self, base_path="/home/nerd/scripting-pdf/shared"):
        self.base_path = Path(base_path)
        self.toc_sections = self.base_path / "toc_sections"
        self.farsi_sections = self.base_path / "farsi_toc_sections"
        self.combined_path = self.base_path / "combined"
        
    def create_combined_directory(self):
        """Ensure combined directory exists"""
        self.combined_path.mkdir(exist_ok=True)
        print(f"✅ Combined directory ready: {self.combined_path}")
        
    def get_file_pairs(self):
        """Identify matching file pairs between directories"""
        english_files = {}
        farsi_files = {}
        
        # Extract file numbers and names from English directory
        for file_path in self.toc_sections.glob("*.md"):
            if file_path.name.startswith("00_"):
                continue  # Skip index files
            match = re.match(r'(\d+)_(.+)\.md', file_path.name)
            if match:
                file_num = match.group(1)
                english_files[file_num] = file_path
        
        # Extract file numbers and names from Farsi directory
        for file_path in self.farsi_sections.glob("*.md"):
            if file_path.name.startswith("00_"):
                continue  # Skip index files
            match = re.match(r'(\d+)_(.+)_farsi\.md', file_path.name)
            if match:
                file_num = match.group(1)
                farsi_files[file_num] = file_path
        
        # Create pairs
        pairs = []
        for file_num in sorted(english_files.keys()):
            if file_num in farsi_files:
                pairs.append({
                    'number': file_num,
                    'english': english_files[file_num],
                    'farsi': farsi_files[file_num]
                })
            else:
                print(f"⚠️  Warning: No Farsi version found for {english_files[file_num].name}")
        
        print(f"📊 Found {len(pairs)} matching file pairs")
        return pairs
        
    def extract_title_from_content(self, content):
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"
        
    def combine_files(self, english_file, farsi_file):
        """Combine individual file pairs"""
        try:
            # Read both files
            with open(english_file, 'r', encoding='utf-8') as f:
                english_content = f.read()
            with open(farsi_file, 'r', encoding='utf-8') as f:
                farsi_content = f.read()
            
            # Extract titles
            english_title = self.extract_title_from_content(english_content)
            farsi_title = self.extract_title_from_content(farsi_content)
            
            # Create combined filename
            file_number = re.match(r'(\d+)_', english_file.name).group(1)
            combined_filename = f"{file_number}_combined.md"
            combined_path = self.combined_path / combined_filename
            
            # Create combined content
            combined_content = f"""# {english_title} / {farsi_title}

**File Number**: {file_number}
**Combined Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🇺🇸 English Version

{english_content}

---

## 🇮🇷 فارسی (Farsi Version)

{farsi_content}

---

*This file combines both English and Farsi versions of the same content.*
"""
            
            # Write combined file
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            print(f"✅ Combined: {combined_filename}")
            return combined_path
            
        except Exception as e:
            print(f"❌ Error combining {english_file.name}: {str(e)}")
            return None
            
    def create_master_index(self, pairs):
        """Create the master combined index file"""
        try:
            # Read original index files for metadata
            english_index_path = self.toc_sections / "00_TOC_INDEX.md"
            farsi_index_path = self.farsi_sections / "00_COMPREHENSIVE_FARSI_INDEX.md"
            
            english_metadata = ""
            farsi_metadata = ""
            
            if english_index_path.exists():
                with open(english_index_path, 'r', encoding='utf-8') as f:
                    english_content = f.read()
                    # Extract metadata lines
                    lines = english_content.split('\n')
                    for line in lines[:10]:  # First 10 lines usually contain metadata
                        if line.startswith('**') or line.startswith('#'):
                            english_metadata += line + '\n'
            
            if farsi_index_path.exists():
                with open(farsi_index_path, 'r', encoding='utf-8') as f:
                    farsi_content = f.read()
                    # Extract metadata lines
                    lines = farsi_content.split('\n')
                    for line in lines[:10]:  # First 10 lines usually contain metadata
                        if line.startswith('**') or line.startswith('#'):
                            farsi_metadata += line + '\n'
            
            # Create master index content
            master_content = f"""# 📚 Combined Bilingual Index / فهرست دوزبانه ترکیبی

**Combination Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Combined Files**: {len(pairs)}

## 📋 Original Metadata

### English Index Metadata
{english_metadata}

### Farsi Index Metadata
{farsi_metadata}

---

## 📄 Combined Files (بر اساس شماره صفحه)

"""
            
            # Add entries for each combined file
            for pair in pairs:
                file_number = pair['number']
                english_title = self.extract_title_from_content(
                    open(pair['english'], 'r', encoding='utf-8').read()
                )
                farsi_title = self.extract_title_from_content(
                    open(pair['farsi'], 'r', encoding='utf-8').read()
                )
                
                master_content += f"""- **Page {file_number}**: [{file_number}_combined.md]({file_number}_combined.md)
  - 🇺🇸 English: {english_title}
  - 🇮🇷 فارسی: {farsi_title}

"""
            
            master_content += f"""
---

## 🔗 Navigation

- **English Original**: [toc_sections/00_TOC_INDEX.md](../toc_sections/00_TOC_INDEX.md)
- **Farsi Original**: [farsi_toc_sections/00_COMPREHENSIVE_FARSI_INDEX.md](../farsi_toc_sections/00_COMPREHENSIVE_FARSI_INDEX.md)

---

*This master index provides access to all combined bilingual files.*
"""
            
            # Write master index
            master_index_path = self.combined_path / "00_COMBINED_INDEX.md"
            with open(master_index_path, 'w', encoding='utf-8') as f:
                f.write(master_content)
            
            print(f"✅ Master index created: {master_index_path.name}")
            return master_index_path
            
        except Exception as e:
            print(f"❌ Error creating master index: {str(e)}")
            return None
            
    def process_all_files(self):
        """Main processing function"""
        print("🚀 Starting file combination process...")
        
        # Step 1: Setup directory
        self.create_combined_directory()
        
        # Step 2: Get file pairs
        pairs = self.get_file_pairs()
        if not pairs:
            print("❌ No file pairs found!")
            return False
        
        # Step 3: Combine individual files
        combined_files = []
        for pair in pairs:
            combined_file = self.combine_files(pair['english'], pair['farsi'])
            if combined_file:
                combined_files.append(combined_file)
        
        # Step 4: Create master index
        master_index = self.create_master_index(pairs)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   • File pairs processed: {len(pairs)}")
        print(f"   • Combined files created: {len(combined_files)}")
        print(f"   • Master index created: {'Yes' if master_index else 'No'}")
        print(f"   • Output directory: {self.combined_path}")
        
        return len(combined_files) > 0

def main():
    """Main execution function"""
    combiner = FileCombiner()
    success = combiner.process_all_files()
    
    if success:
        print("\n🎉 File combination completed successfully!")
    else:
        print("\n❌ File combination failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
