import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

html = open(r'C:\Users\alexa\.gemini\antigravity-ide\brain\e6dbae8b-d50c-4af2-bcfb-ed4d3d3d9092\google_hotels_debug.html', encoding='utf-8').read()
text = re.sub(r'<[^>]+>', ' ', html)
# Normaliza espacos em branco
text = re.sub(r'\s+', ' ', text)

print(f"Total R$: {text.count('R$')}")

matches = re.findall(r'.{0,60}R\$.{0,40}', text)
for m in matches[:15]:
    print(m)
