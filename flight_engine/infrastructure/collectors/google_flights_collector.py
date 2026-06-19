from domain.entities import Flight
from infrastructure.collectors.base_collector import BaseCollector
from datetime import datetime
from decimal import Decimal
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class GoogleFlightsCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="GoogleFlights(Real)")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int
    ) -> list[Flight]:
        date_str = departure_date.strftime("%Y-%m-%d")
        url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date_str}%20oneway&hl=pt-BR&curr=BRL"
        
        flights = []
        async with async_playwright() as p:
            # Iniciando Chromium em modo Headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="pt-BR"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"[{self.name}] Acessando {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Aguardando renderização do JS do Google Flights
                await page.wait_for_timeout(5000)
                
                # Buscando os elementos da lista de voos (O Google Flights agrupa em LIs)
                items = await page.query_selector_all("li")
                
                for item in items:
                    text = await item.inner_text()
                    # Filtro rudimentar para achar cards que contenham preço e tempo
                    if "R$" in text and ("min" in text or "h" in text):
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        
                        # Extraindo o preço
                        price_line = next((l for l in lines if "R$" in l), None)
                        if not price_line: continue
                        
                        # Limpando o valor monetário: "R$ 1.500" -> "1500"
                        price_str = price_line.replace("R$", "").replace(".", "").replace(",", ".").strip()
                        try:
                            price_val = Decimal(price_str)
                        except:
                            continue
                            
                        # Extraindo a companhia aérea (geralmente é o texto logo após o horário)
                        # Como o DOM é mutável, tentaremos pegar uma das primeiras linhas de texto
                        airline = lines[1] if len(lines) > 1 else "Unknown Airline"
                        
                        # Impedir lixo de outras LIs (ex: rodapé)
                        if len(airline) > 30: continue
                            
                        flights.append(Flight(
                            airline=airline,
                            origin=origin,
                            destination=destination,
                            departure_date=departure_date,
                            arrival_date=departure_date, # Simplificado para PoC
                            price=price_val,
                            currency="BRL",
                            base_price_brl=price_val,
                            duration=120, # Simplificado
                            stops=0,
                            cabin_class="ECONOMY",
                            booking_url=url
                        ))
                        
                        # Limitando a 5 resultados para o PoC não demorar tanto
                        if len(flights) >= 5:
                            break
                            
            except Exception as e:
                logger.error(f"[{self.name}] Erro no scraping: {e}")
            finally:
                await browser.close()
                
        return flights
