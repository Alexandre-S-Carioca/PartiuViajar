from domain.entities import Flight
from infrastructure.collectors.base_collector import BaseCollector
from datetime import datetime
from decimal import Decimal
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

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
                
                # Lógica rudimentar de extração para o PoC: 
                # Buscamos as linhas que começam com R$
                for i, line in enumerate(lines):
                    if line.startswith("R$") and len(line) < 15:
                        price_str = line.replace("R$", "").replace(".", "").replace(",", ".").strip()
                        try:
                            price_val = Decimal(price_str)
                            
                            # Tenta pegar um provável nome de companhia nas linhas anteriores.
                            # O Kayak mostra a companhia aérea na linha imediatamente antes do preço (i-1)
                            # ou nas linhas anteriores a ela, se houver anúncios/tags intermediárias.
                            airline_candidate = "Múltiplas/Kayak"
                            for offset in range(1, 5):
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
                                    cand.startswith("R$") or
                                    any(x in cand for x in ["Ver oferta", "Basic", "Pinto Martins", "Internacional"])
                                ):
                                    continue
                                airline_candidate = cand
                                break
                                
                            flights.append(Flight(
                                airline=airline_candidate,
                                origin=origin,
                                destination=destination,
                                departure_date=departure_date,
                                arrival_date=departure_date,
                                price=price_val,
                                currency="BRL",
                                base_price_brl=price_val,
                                duration=180, # Fixo para PoC
                                stops=1,      # Fixo para PoC
                                cabin_class="ECONOMY",
                                booking_url=url
                            ))
                            
                            if len(flights) >= 5: # Limitando a 5 resultados
                                break
                        except Exception as parse_e:
                            continue
                            
            except Exception as e:
                logger.error(f"[{self.name}] Erro no scraping: {e}")
            finally:
                await browser.close()
                
        return flights
