
import asyncio
from infrastructure.clients.scrapestack_client import scrapestack_client

async def test():
    url = 'https://b2c.voegol.com.br/compra/busca-parceiros?tipo=1&ida=01-07-2026&origem=FOR&destino=REC&adultos=1'
    print(f'Testando Scrapestack na URL: {url}')
    html = await scrapestack_client.scrape_html(url, render_js=True, premium_proxy=True)
    if html:
        with open('gol_deep.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'HTML salvo! Tamanho: {len(html)} bytes')
    else:
        print('Falha ao raspar HTML')

if __name__ == '__main__':
    asyncio.run(test())

