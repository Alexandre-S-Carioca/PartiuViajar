import asyncio
import re
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

def parse_stops_google(s: str) -> int:
    s = s.lower().strip()
    if "sem escalas" in s or "direto" in s or "sem escala" in s:
        return 0
    match = re.search(r'(\d+)\s*parada', s)
    if match:
        return int(match.group(1))
    return 0

async def inspect():
    url = "https://www.google.com/travel/flights?q=Flights%20to%20SCL%20from%20FOR%20on%202026-07-01%20oneway&hl=pt-BR&curr=BRL"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = await context.new_page()
        try:
            print("Accessing", url)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(8000)
            
            items = await page.query_selector_all("li")
            print(f"Total list items (li): {len(items)}")
            
            for item in items:
                text = await item.inner_text()
                if "R$" in text and ("min" in text or "h" in text):
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    price_val = None
                    duration = None
                    stops = 0
                    actual_origin = None
                    actual_destination = None
                    airline = "Unknown"
                    
                    # 1. Price
                    price_line = next((l for l in lines if "R$" in l), None)
                    if price_line:
                        price_str = price_line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                        try:
                            price_val = Decimal(price_str)
                        except:
                            pass
                            
                    # 2. Duration
                    for line in lines:
                        if re.search(r'^\d+\s*h(\s*\d+\s*min)?$', line) or re.search(r'^\d+\s*min$', line):
                            duration = parse_duration(line)
                            break
                            
                    # 3. Stops
                    for line in lines:
                        if "escala" in line.lower() or "parada" in line.lower() or "direto" in line.lower():
                            stops = parse_stops_google(line)
                            break
                            
                    # 4. Route/Airports
                    for line in lines:
                        match = re.search(r'^([A-Z]{3})[^A-Za-z]+([A-Z]{3})$', line)
                        if match:
                            actual_origin = match.group(1)
                            actual_destination = match.group(2)
                            break
                            
                    # 5. Airline (first line that is not time, duration, stops, route, price)
                    for line in lines:
                        is_time = (":" in line and any(c.isdigit() for c in line))
                        is_duration = re.search(r'^\d+\s*h(\s*\d+\s*min)?$', line) or re.search(r'^\d+\s*min$', line)
                        is_stops = "escala" in line.lower() or "parada" in line.lower() or "direto" in line.lower()
                        is_route = re.search(r'^([A-Z]{3})[^A-Za-z]+([A-Z]{3})$', line)
                        is_price = "R$" in line
                        is_carbon = "co2" in line.lower() or "emiss" in line.lower()
                        if not any([is_time, is_duration, is_stops, is_route, is_price, is_carbon, line == "–"]):
                            airline = line
                            break
                    
                    if "Operado" in airline:
                        airline = airline.split("Operado")[0].strip()
                    airline = airline.rstrip(",").strip()
                    
                    print(f"Flight Found -> Price: R$ {price_val} | Airline: {airline} | Duration: {duration} mins | Stops: {stops} | Origin: {actual_origin} | Destination: {actual_destination}")
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
