import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.collectors.kayak_collector import KayakCollector

async def main():
    collector = KayakCollector()
    dep_date = datetime.now() + timedelta(days=30)
    flights = await collector.fetch_flights("FOR", "CGH", dep_date, 1)
    
    print(f"Found {len(flights)} flights")
    for f in flights:
        print(f"{f.airline} | {f.departure_date.strftime('%H:%M')} - {f.arrival_date.strftime('%H:%M')} | {f.origin} -> {f.destination} ({f.duration}m) | R$ {f.price}")

async def main_debug():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        date_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        url = f"https://www.kayak.com.br/flights/FOR-CGH/{date_str}?sort=price_a"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)
        content = await page.evaluate("document.body.innerText")
        lines = [line.strip() for line in content.split('\\n') if line.strip()]
        
        with open("kayak_dom_dump.txt", "w", encoding="utf-8") as f:
            for i, line in enumerate(lines):
                f.write(f"[{i}]: {line}\\n")
        
        print("DOM dumped to kayak_dom_dump.txt")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main_debug())
