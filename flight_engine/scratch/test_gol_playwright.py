import asyncio
from playwright.async_api import async_playwright

async def test_gol():
    url = "https://www.voegol.com.br/br/voos-nacionais?gclsrc=aw.ds&gad_source=1&gad_campaignid=12520896889&gbraid=0AAAAADyStcK15rEYtcLfqcKqmdf7dY28r&gclid=Cj0KCQjwo_PRBhDNARIsAEcVALXPUpQzNOdXgwpMCAxTWJv-Mvc8KbhexDLCc40Jnsouj1QbU5mj1hcaAtW-EALw_wcB"
    
    print(f"Iniciando testes no GOL...\nURL: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = await context.new_page()
        
        try:
            print("Acessando a pagina...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("Aguardando 10s para carregar...")
            await asyncio.sleep(10)
            
            await page.screenshot(path="gol_initial.png")
            print("Screenshot salva em gol_initial.png")
            
            # Tentar fechar modais de cookies se existirem
            try:
                await page.click("button:has-text('Aceitar')", timeout=5000)
            except:
                pass
                
            print("Preenchendo origem FOR...")
            # Click no campo de origem
            await page.click("input[id*='origin']")
            await page.fill("input[id*='origin']", "FOR")
            await asyncio.sleep(1)
            await page.press("input[id*='origin']", "Enter")
            
            print("Preenchendo destino REC...")
            await page.click("input[id*='destination']")
            await page.fill("input[id*='destination']", "REC")
            await asyncio.sleep(1)
            await page.press("input[id*='destination']", "Enter")
            
            # Aqui deveríamos preencher datas e clicar em buscar, mas GOL muda as classes frequentemente
            # Vamos printar a tela atual com origem e destino para ver se preencheu
            await page.screenshot(path="gol_filled.png")
            print("Screenshot salva em gol_filled.png com os campos preenchidos.")
            
        except Exception as e:
            print(f"Erro durante o teste: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_gol())
