import logging
from typing import List
from datetime import datetime
from decimal import Decimal
import re

from playwright.async_api import async_playwright

from domain.entities import Flight
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.clients.scrapestack_client import scrapestack_client
from core.feature_flags import feature_flags

logger = logging.getLogger(__name__)

class GolScrapestackCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="GOL(Scrapestack)")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"
    ) -> List[Flight]:
        if not feature_flags.ENABLE_GOL:
            logger.info(f"[{self.name}] Coletor desativado via feature flag.")
            return []

        # Formato de Deep Link da GOL (B2C SPA)
        date_str = departure_date.strftime("%d-%m-%Y")
        url = f"https://b2c.voegol.com.br/compra/busca-parceiros?tipo=1&ida={date_str}&origem={origin}&destino={destination}&adultos={adults}"
        
        logger.info(f"[{self.name}] Solicitando HTML via Scrapestack para {url}")
        
        # Requer render_js=True pois a GOL é um SPA (Angular)
        html_content = await scrapestack_client.scrape_html(url, render_js=True, premium_proxy=True)
        
        if not html_content:
            logger.error(f"[{self.name}] Scrapestack falhou ou retornou vazio.")
            return []
            
        if "Please enable JavaScript" in html_content and "app-root" in html_content:
            logger.error(f"[{self.name}] A API Key do Scrapestack não conseguiu renderizar JS (Plano Free?).")
            return []

        flights = []
        
        # Parse do DOM retornado
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Injeta o HTML estático
                await page.set_content(html_content, wait_until="load")
                
                # Exemplo de seletores genéricos da GOL (Variam muito e requerem manutenção)
                # Como a GOL muda as classes, tentamos encontrar cards com preço
                flight_cards = await page.query_selector_all(".flight-card, div[data-test-id='flight-card']")
                
                if not flight_cards:
                    # Tenta fallback para busca de textos puros com R$
                    texts = await page.evaluate("() => document.body.innerText")
                    if "R$" in texts:
                        logger.warning(f"[{self.name}] Voos encontrados no texto, mas os seletores falharam.")
                
                for card in flight_cards:
                    text = await card.inner_text()
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    price_line = next((l for l in lines if "R$" in l), None)
                    if not price_line: continue
                    
                    price_str = price_line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                    try:
                        price_val = Decimal(price_str)
                    except:
                        continue
                        
                    duration_val = 120 # Fallback
                    
                    flights.append(Flight(
                        airline="GOL",
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        arrival_date=departure_date,
                        price=price_val,
                        currency="BRL",
                        base_price_brl=price_val,
                        duration=duration_val,
                        stops=0,
                        cabin_class="Economy",
                        booking_url=url,
                        collected_at=datetime.utcnow(),
                        id=f"gol_scrapestack_{origin}_{destination}_{int(price_val)}"
                    ))
                    
            except Exception as e:
                logger.error(f"[{self.name}] Falha na extração de dados com Playwright virtual: {str(e)}")
            finally:
                await browser.close()
                
        logger.info(f"[{self.name}] Encontrou {len(flights)} voos.")
        return flights
