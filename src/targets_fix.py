""" Run this script to convert accented characters in targets.txt to English equivalents. """

import unicodedata

# Path to your targets.txt file
input_file = r"C:\Users\JASMINE\Desktop\RnD_asteroid\targets.txt"
output_file = input_file.replace(".txt", "_english.txt")

def to_english(text):
    # Normalize accented characters → plain ASCII (e.g., é → e)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
converted = [to_english(line) for line in lines]
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(converted)
print(f"✅ Conversion complete!\nSaved as: {output_file}")
