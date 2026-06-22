import asyncio
from playwright.async_api import async_playwright

async def main():
    city = "Sao Paulo"
    url = f"https://www.booking.com/searchresults.pt-br.html?ss={city.replace(' ', '+')}"
    print(f"Iniciando scraper Booking.com: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            
            # Check if there's a property card
            cards = await page.query_selector_all("div[data-testid='property-card']")
            print(f"Cards found: {len(cards)}")
            
            for card in cards[:5]:
                try:
                    name_el = await card.query_selector("div[data-testid='title']")
                    name = await name_el.inner_text() if name_el else "Unknown"
                    
                    price_el = await card.query_selector("span[data-testid='price-and-discounted-price']")
                    price = await price_el.inner_text() if price_el else "0"
                    
                    rating_el = await card.query_selector("div[data-testid='review-score'] div")
                    rating = await rating_el.inner_text() if rating_el else "0.0"
                    
                    print(f"Name: {name} | Price: {price} | Rating: {rating}")
                    if card == cards[0]:
                        text = await card.inner_text()
                        print(f"--- CARD TEXT ---\n{text}\n-----------------")
                except Exception as e:
                    print(f"Error parsing card: {e}")
                    
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
