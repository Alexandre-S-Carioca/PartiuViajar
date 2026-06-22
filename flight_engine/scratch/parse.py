import bs4
html=open(r'C:\Users\alexa\.gemini\antigravity-ide\brain\e6dbae8b-d50c-4af2-bcfb-ed4d3d3d9092\google_hotels_debug.html', encoding='utf-8').read()
soup=bs4.BeautifulSoup(html, 'html.parser')
print('Divs listitem:', len(soup.find_all('div', attrs={'role': 'listitem'})))
print('c-wiz elements:', len(soup.find_all('c-wiz')))
tags = soup.find_all('a')
prices = [a for a in tags if 'R$' in a.text]
print('A tags with price:', len(prices))
if prices:
    for i in range(min(3, len(prices))):
        print(f"--- Hotel {i} ---")
        lines = [line.strip() for line in prices[i].text.split('\n') if line.strip()]
        for line in lines:
            print(line)
