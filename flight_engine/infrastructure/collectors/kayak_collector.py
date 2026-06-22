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

def is_stops_line(s: str) -> bool:
    s = s.lower().strip()
    return bool(re.search(r'^\d+\s*escala', s) or s == "direto" or s.startswith("sem escala") or s.endswith("escalas"))

def parse_stops(s: str) -> int:
    s = s.lower().strip()
    if "direto" in s or "sem escala" in s:
        return 0
    match = re.search(r'(\d+)\s*escala', s)
    if match:
        return int(match.group(1))
    return 0

class KayakCollector(BaseCollector):
    def __init__(self):
        super().__init__(name="Kayak(Real)")

    async def fetch_flights(
        self, origin: str, destination: str, departure_date: datetime, adults: int
    ) -> list[Flight]:
        date_str = departure_date.strftime("%Y-%m-%d")
        # URL do Kayak para busca Oneway, ordenado por preço
        url = f"https://www.kayak.com.br/flights/{origin}-{destination}/{date_str}?sort=price_a"
        
        flights = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="pt-BR"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"[{self.name}] Acessando {url}")
                # Kayak tem popups e carregamentos pesados, aguardamos domcontentloaded
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Aguarda bastante tempo para o loader do aviãozinho do Kayak terminar
                await page.wait_for_timeout(8000)
                
                # Vamos pegar todo o texto visível da página
                content = await page.evaluate("document.body.innerText")
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Lógica de extração:
                # Buscamos as linhas que começam com R$
                for i, line in enumerate(lines):
                    if line.startswith("R$") and len(line) < 15:
                        price_str = line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                        try:
                            price_val = Decimal(price_str)
                            
                            # Buscar retroativamente detalhes: duração, escalas, aeroportos
                            duration_val = 180  # fallback
                            stops_val = 1      # fallback
                            actual_origin = origin
                            actual_destination = destination
                            departure_datetime = departure_date
                            
                            search_range = range(max(0, i - 15), i)
                            
                            # Duração
                            for j in reversed(search_range):
                                cand = lines[j]
                                if re.search(r'^\d+h(\s*\d+min)?$', cand) or re.search(r'^\d+min$', cand):
                                    duration_val = parse_duration(cand)
                                    break
                            
                            # Escalas
                            for j in reversed(search_range):
                                cand = lines[j]
                                if is_stops_line(cand):
                                    stops_val = parse_stops(cand)
                                    break
                                    
                            # Aeroportos de partida e destino reais
                            for j in reversed(search_range):
                                if lines[j] == "-":
                                    dep_cand = lines[j-1]
                                    dest_cand = lines[j+1]
                                    if len(dep_cand) >= 3 and dep_cand[:3].isupper() and dep_cand[:3].isalpha():
                                        actual_origin = dep_cand[:3]
                                    if len(dest_cand) >= 3 and dest_cand[:3].isupper() and dest_cand[:3].isalpha():
                                        actual_destination = dest_cand[:3]
                                    break
                                    
                            # Horário exato de partida
                            for j in reversed(search_range):
                                if re.search(r'\d{1,2}:\d{2}\s*.\s*\d{1,2}:\d{2}', lines[j]):
                                    times = re.findall(r'(\d{1,2}):(\d{2})', lines[j])
                                    if len(times) >= 2:
                                        dep_hour, dep_min = map(int, times[0])
                                        departure_datetime = departure_date.replace(hour=dep_hour, minute=dep_min)
                                    break
                                    
                            arrival_datetime = departure_datetime + timedelta(minutes=duration_val)

                            # Tenta pegar um provável nome de companhia nas linhas anteriores.
                            airline_candidate = "Múltiplas/Kayak"
                            for offset in range(1, 10):
                                idx_cand = i - offset
                                if idx_cand < 0:
                                    break
                                cand = lines[idx_cand]
                                if (
                                    "min" in cand or 
                                    "h" in cand or 
                                    "escala" in cand or 
                                    "parada" in cand or 
                                    "Anúncio" in cand or 
                                    "Anuncio" in cand or 
                                    cand == "|" or 
                                    cand == "-" or
                                    cand.startswith("R$") or
                                    any(x in cand.lower() for x in ["ver oferta", "basic", "pinto martins", "internacional", "selecionar", "econômica", "economica", "plus", "direto"])
                                    or (len(cand) >= 3 and cand[:3].isupper() and cand[:3].isalpha() and len(cand) > 3 and cand[3].islower())
                                ):
                                    continue
                                airline_candidate = cand
                                break
                                
                            # Validar se o voo é válido
                            bad_airlines = ["direto", "escala", "parada", "fortaleza", "santiago", "pinto martins", "arturo merino", "selecionar", "basic", "plus", "econômica", "economica", "oferta", "decolar", "todas as"]
                            if any(x in airline_candidate.lower() for x in bad_airlines) or len(airline_candidate) > 30:
                                continue

                            flights.append(Flight(
                                airline=airline_candidate,
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
                            
                            if len(flights) >= 5: # Limitando a 5 resultados
                                break
                        except Exception as parse_e:
                            logger.error(f"[{self.name}] Erro no parse de voo: {parse_e}")
                            continue
                            
            except Exception as e:
                logger.error(f"[{self.name}] Erro no scraping: {e}")
            finally:
                await browser.close()
                
        return flights

