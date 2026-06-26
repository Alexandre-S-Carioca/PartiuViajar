import asyncio
import os
import sys

# Garantir que o diretório raiz esteja no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from infrastructure.clients.scrapestack_client import scrapestack_client

async def fetch_gol_deep():
    url = "https://b2c.voegol.com.br/compra/busca-parceiros?tipo=1&ida=01-07-2026&origem=FOR&destino=REC&adultos=1"
    print(f"Buscando: {url}")
    
    html = await scrapestack_client.scrape_html(url, render_js=False, premium_proxy=False)
    if html:
        with open("gol_deep_source.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Sucesso! {len(html)} bytes gravados em gol_deep_source.html")
        if "Acesso Negado" in html or "Access Denied" in html:
            print("⚠️ Fomos bloqueados pelo proxy/Scrapestack.")
        else:
            print("HTML parece válido.")
    else:
        print("Erro na requisição.")

if __name__ == "__main__":
    asyncio.run(fetch_gol_deep())
