from domain.entities import Flight
from infrastructure.collectors.base_collector import BaseCollector
from infrastructure.clients.scrapestack_client import scrapestack_client
from infrastructure.collectors.google_flights_collector import parse_duration, parse_stops_google
from datetime import datetime
from decimal import Decimal
import logging
import re
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class GoogleFlightsScrapestackCollector(BaseCollector):
    def __init__(self):
        # Nome distinto para rodar em paralelo sem conflitar no Registry
        super().__init__(name="GoogleFlights(Scrapestack)")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"
    ) -> list[Flight]:
        date_str = departure_date.strftime("%Y-%m-%d")
        # Mesma URL utilizada na busca nativa
        url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date_str}%20oneway&hl=pt-BR&curr={currency}"
        
        logger.info(f"[{self.name}] Solicitando HTML via Scrapestack para {url}")
        
        # 1. Faz a requisição pelo Scrapestack
        html_content = await scrapestack_client.scrape_html(url, render_js=True, premium_proxy=True)
        
        if not html_content:
            logger.error(f"[{self.name}] Scrapestack falhou ou retornou vazio.")
            return []

        flights = []
        
        # 2. Usa o Playwright apenas como um "parser local" de DOM super rápido, sem ir na rede
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Injeta o HTML retornado pela API na página virtual
                await page.set_content(html_content, wait_until="load")
                
                # 3. Reaproveitamos 100% da lógica original baseada nos seletores do Google
                items = await page.query_selector_all("li")
                
                for item in items:
                    text = await item.inner_text()
                    if "R$" in text and ("min" in text or "h" in text):
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        
                        # Extraindo o preço
                        price_line = next((l for l in lines if "R$" in l), None)
                        if not price_line: continue
                        
                        price_str = price_line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                        try:
                            price_val = Decimal(price_str)
                        except:
                            continue
                            
                        # Extraindo a duração
                        duration_val = 120
                        for line in lines:
                            if re.search(r'^\d+\s*h(\s*\d+\s*min)?$', line) or re.search(r'^\d+\s*min$', line):
                                duration_val = parse_duration(line)
                                break
                                
                        # Extraindo paradas
                        stops_val = 0
                        for line in lines:
                            if "escala" in line.lower() or "parada" in line.lower() or "direto" in line.lower():
                                stops_val = parse_stops_google(line)
                                break
                                
                        # Extraindo aeroportos
                        actual_origin = origin
                        actual_destination = destination
                        for line in lines:
                            match = re.search(r'^([A-Z]{3})[^A-Za-z]+([A-Z]{3})$', line)
                            if match:
                                actual_origin = match.group(1)
                                actual_destination = match.group(2)
                                break
                                
                        flights.append(Flight(
                            airline="Múltiplas" if "Múltiplas companhias aéreas" in text else lines[0],
                            origin=actual_origin,
                            destination=actual_destination,
                            departure_date=departure_date,
                            arrival_date=departure_date, # simplified
                            price=price_val,
                            currency="BRL",
                            base_price_brl=price_val,
                            duration=duration_val,
                            stops=stops_val,
                            cabin_class="Economy",
                            booking_url=url,
                            collected_at=datetime.utcnow(),
                            id=f"gflight_scrapestack_{actual_origin}_{actual_destination}_{int(price_val)}"
                        ))
                        
            except Exception as e:
                logger.error(f"[{self.name}] Falha na extração de dados com Playwright virtual: {str(e)}")
            finally:
                await browser.close()
                
        logger.info(f"[{self.name}] Encontrou {len(flights)} voos.")
        return flights
