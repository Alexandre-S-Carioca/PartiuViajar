from domain.entities import Flight
from infrastructure.collectors.base_collector import BaseCollector
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import re
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

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

class GoogleFlightsCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="GoogleFlights(Real)")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"
    ) -> list[Flight]:
        date_str = departure_date.strftime("%Y-%m-%d")
        url = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date_str}%20oneway&hl=pt-BR&curr={currency}"
        
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
                        
                        price_str = price_line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                        try:
                            price_val = Decimal(price_str)
                        except:
                            continue
                            
                        # Extraindo a duração
                        duration_val = 120  # fallback
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
                                
                        # Extraindo aeroportos de partida e destino reais da rota
                        actual_origin = origin
                        actual_destination = destination
                        for line in lines:
                            match = re.search(r'^([A-Z]{3})[^A-Za-z]+([A-Z]{3})$', line)
                            if match:
                                actual_origin = match.group(1)
                                actual_destination = match.group(2)
                                break
                                
                        # Extraindo horários reais e ajustando datas
                        departure_datetime = departure_date
                        if len(lines) > 0:
                            time_match = re.search(r'(\d{2}):(\d{2})', lines[0])
                            if time_match:
                                hour = int(time_match.group(1))
                                minute = int(time_match.group(2))
                                departure_datetime = departure_date.replace(hour=hour, minute=minute)
                                
                        arrival_datetime = departure_datetime + timedelta(minutes=duration_val)
                        
                        # Extraindo a companhia aérea
                        airline = "Unknown Airline"
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
                        
                        if len(airline) > 30: continue
                            
                        flights.append(Flight(
                            airline=airline,
                            origin=actual_origin,
                            destination=actual_destination,
                            departure_date=departure_datetime,
                            arrival_date=arrival_datetime,
                            price=price_val,
                            currency="BRL",
                            base_price_brl=price_val,
                            duration=duration_val,
                            stops=stops_val,
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

