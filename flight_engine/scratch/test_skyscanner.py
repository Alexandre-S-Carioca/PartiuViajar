import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://www.skyscanner.com.br/"
    
    screenshot_path = "C:/Users/alexa/.gemini/antigravity-ide/brain/9a046d1c-4604-4d0f-a099-a96a77b5ec8d/skyscanner_test.png"
    html_path = "C:/Users/alexa/.gemini/antigravity-ide/brain/9a046d1c-4604-4d0f-a099-a96a77b5ec8d/skyscanner_test.html"

    async with async_playwright() as p:
        # Launching Chromium with some stealth-like configurations
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Setting a random webdriver flag to false to bypass basic bot detections
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Acessando URL: {url}")
        response = await page.goto(url, wait_until="networkidle", timeout=60000)
        
        print(f"Status HTTP: {response.status if response else 'N/A'}")
        
        # Wait for potential Cloudflare challenge to pass (or fail)
        await page.wait_for_timeout(8000)
        
        # Tirar Screenshot
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot salva em: {screenshot_path}")
        
        # Salvar HTML
        content = await page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"HTML salvo em: {html_path}")
        
        title = await page.title()
        print(f"Título da página: {title}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
