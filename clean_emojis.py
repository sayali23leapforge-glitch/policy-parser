#!/usr/bin/env python3
import re

# Read the file
with open('d:\\Auto dashboard\\backend\\pdf_parser.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count emojis before
emoji_count_before = len(re.findall(r'[✓❌⚠️📄🔄🔗→ℹ-]', content))

# Remove/replace all emojis
replacements = {
    '\u2705': '[OK]',  # ✓
    '\u274C': '[ERROR]',  # ❌
    '\u26A0\uFE0F': '[WARNING]',  # ⚠️
    '\U0001F4C4': '[PDF]',  # 📄
    '\U0001F504': '[REFRESH]',  # 🔄
    '\U0001F517': '[LINK]',  # 🔗
    '\u2192': '->',  # →
    '\u2139': '[INFO]',  # ℹ
}

for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Write back
with open('d:\\Auto dashboard\\backend\\pdf_parser.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Cleaned all emojis from pdf_parser.py')
