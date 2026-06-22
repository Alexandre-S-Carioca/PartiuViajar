import asyncio
import re
from datetime import datetime
from decimal import Decimal
from playwright.async_api import async_playwright

def parse_duration(s: str) -> int:
    s = s.replace(" ", "").lower()
    hours = 0
    minutes = 0
    match_h = re.search(r'(\d+)h', s)
    if match_h:
        hours = int(match_h.group(1))
    match_m = re.search(r'(\d+)min', s)
    if match_m:
        minutes = int(match_m.group(1))
    return hours * 60 + minutes

def is_stops_line(s: str) -> bool:
    s = s.lower().strip()
    return bool(re.search(r'^\d+\s*escala', s) or s == "direto" or s.startswith("sem escala") or s.endswith("escalas"))

def parse_stops(s: str) -> int:
    s = s.lower().strip()
    if "direto" in s or "sem escala" in s:
        return 0
    match = re.search(r'(\d+)\s*escala', s)
    if match:
        return int(match.group(1))
    return 0

async def inspect():
    url = "https://www.kayak.com.br/flights/FOR-SCL/2026-11-22?sort=price_a"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = await context.new_page()
        try:
            print("Accessing", url)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(10000)
            
            content = await page.evaluate("document.body.innerText")
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            print(f"Total lines: {len(lines)}")
            for i, line in enumerate(lines):
                if line.startswith("R$") and len(line) < 15:
                    price_str = line.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        price_val = Decimal(price_str)
                    except:
                        continue
                    
                    print(f"\n--- Found price line {price_val} at index {i} ---")
                    start = max(0, i - 18)
                    end = min(len(lines), i + 3)
                    for j in range(start, end):
                        marker = ">>>" if j == i else "   "
                        print(f"{marker} {j}: {lines[j]}")
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
