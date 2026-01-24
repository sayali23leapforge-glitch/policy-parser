#!/usr/bin/env python3
"""Debug KOL regex directly"""
import re

test_text = """KOL16 - Other Property Damage to insured vehicle: $7,794.00 (Loss); $0.00 (Expense);
KOL18 - Loss of use: $301.00 (Loss); $0.00 (Expense);"""

print("Test text:")
print(repr(test_text))
print("\n" + "=" * 80)

# Current regex
kol_pattern = r'(KOL\d+\s*[-–]\s*[^\n:]+?):\s*\$\s*([\d,\.]+)\s*\(Loss\);\s*\$\s*([\d,\.]+)\s*\(Expense\);'
matches = re.findall(kol_pattern, test_text, re.IGNORECASE)

print(f"Current regex found {len(matches)} matches:")
for desc, loss, expense in matches:
    print(f"  • {desc}: ${loss} (L), ${expense} (E)")

print("\n" + "=" * 80)
print("Pattern breakdown:")
print(f"Pattern: {kol_pattern}")
print("=" * 80)

# Test with a simpler pattern
kol_pattern2 = r'(KOL\d+.*?):\s*\$\s*([\d,\.]+)\s*\(Loss\);\s*\$\s*([\d,\.]+)\s*\(Expense\);'
matches2 = re.findall(kol_pattern2, test_text, re.IGNORECASE)
print(f"\nSimpler pattern found {len(matches2)} matches:")
for desc, loss, expense in matches2:
    print(f"  • {desc}: ${loss} (L), ${expense} (E)")

