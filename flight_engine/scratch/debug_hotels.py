import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    url = "https://www.google.com/travel/search?q=hoteis%20em%20SAO&hl=pt-BR&curr=BRL"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={'width': 1280, 'height': 1024}
        )
        page = await context.new_page()
        print("Acessando...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        print("Tirando screenshot...")
        
        # Save to artifact directory
        artifact_dir = r"C:\Users\alexa\.gemini\antigravity-ide\brain\e6dbae8b-d50c-4af2-bcfb-ed4d3d3d9092"
        await page.screenshot(path=os.path.join(artifact_dir, "google_hotels_debug.png"), full_page=True)
        
        # Save HTML
        html = await page.content()
        with open(os.path.join(artifact_dir, "google_hotels_debug.html"), "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()
        print("Finalizado!")

if __name__ == "__main__":
    asyncio.run(main())
