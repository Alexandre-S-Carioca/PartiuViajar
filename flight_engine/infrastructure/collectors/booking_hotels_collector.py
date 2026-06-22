import logging
import re
import uuid
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class BookingHotelsCollector:
    def __init__(self):
        self.name = "Booking(Real)"

    async def fetch_hotels(self, city: str) -> list[dict]:
        """
        Scrape hotels from Booking.com based on city code or name.
        Returns a list of raw hotel dictionaries.
        """
        # Formata URL de busca com datas futuras para forcar o Booking a mostrar os precos
        import datetime
        dt1 = datetime.datetime.now() + datetime.timedelta(days=30)
        dt2 = dt1 + datetime.timedelta(days=1)
        checkin = dt1.strftime("%Y-%m-%d")
        checkout = dt2.strftime("%Y-%m-%d")
        url = f"https://www.booking.com/searchresults.pt-br.html?ss={city.replace(' ', '+')}&checkin={checkin}&checkout={checkout}&group_adults=1&no_rooms=1"
        
        hotels = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="pt-BR"
            )
            page = await context.new_page()
            
            try:
                logger.info(f"[{self.name}] Acessando {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                cards = await page.query_selector_all("div[data-testid='property-card']")
                logger.info(f"[{self.name}] {len(cards)} cards encontrados na pagina.")
                
                seen_names = set()

                for card in cards:
                    try:
                        # Extrai o nome
                        name_el = await card.query_selector("div[data-testid='title']")
                        name = await name_el.inner_text() if name_el else None
                        
                        if not name or name in seen_names:
                            continue
                            
                        # Pega todo o texto do cartao para aplicar regex de preco e rating
                        text = await card.inner_text()
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        
                        # Extrai preco
                        price_val = 0.0
                        for line in lines:
                            if line.startswith("R$"):
                                clean = line.replace("R$", "").replace(".", "").replace(",", ".").replace("\xa0", "").strip()
                                try:
                                    price_val = float(clean)
                                    break
                                except:
                                    pass
                                    
                        if price_val < 50 or price_val > 10000:
                            # Tenta com outra heuristica
                            match = re.search(r'R\$\s*([\d.,]+)', text)
                            if match:
                                try:
                                    price_val = float(match.group(1).replace(".", "").replace(",", "."))
                                except:
                                    pass
                        
                        if price_val < 50:
                            continue # Pula se nao achou preco real

                        # Extrai rating
                        rating = 4.0
                        rating_match = re.search(r'(\d[,.]\d)\s', text)
                        if rating_match:
                            rating = float(rating_match.group(1).replace(",", "."))
                            
                        # Extrai reviews count
                        reviews = 100
                        rev_match = re.search(r'([\d.,]+)\s+avalia', text.lower())
                        if rev_match:
                            try:
                                reviews = int(rev_match.group(1).replace(".", "").replace(",", ""))
                            except:
                                pass

                        # Descobre as estrelas baseado no preco ou nome
                        stars = 3
                        if "Resort" in name: stars = 5
                        elif "Hostel" in name: stars = 2
                        elif "Pousada" in name: stars = 3
                        elif price_val > 800: stars = 5
                        elif price_val > 400: stars = 4

                        # Definir tipo
                        acc_type = "hotel"
                        if "resort" in name.lower(): acc_type = "resort"
                        elif "hostel" in name.lower(): acc_type = "hostel"
                        elif "pousada" in name.lower(): acc_type = "pousada"
                        elif "apart" in name.lower(): acc_type = "pousada"
                        
                        # Extrai foto
                        photo_url = f"https://source.unsplash.com/600x400/?{acc_type},room,bed"
                        img_el = await card.query_selector("img[data-testid='image']")
                        if img_el:
                            src = await img_el.get_attribute("src")
                            if src: photo_url = src

                        hotels.append({
                            "id": str(uuid.uuid4()),
                            "name": name,
                            "type": acc_type,
                            "rating": rating,
                            "stars": stars,
                            "reviews_count": reviews,
                            "price_per_night": price_val,
                            "photo_url": photo_url,
                            "amenities": ["Wi-Fi Gratuito", "Ar-condicionado"] + (["Piscina"] if stars >= 4 else []),
                            "city": city
                        })
                        seen_names.add(name)
                        
                        if len(hotels) >= 20: 
                            break
                            
                    except Exception as e:
                        logger.error(f"[{self.name}] Erro lendo card: {e}")
                        continue
                            
            except Exception as e:
                logger.error(f"[{self.name}] Erro no scraping: {e}")
            finally:
                await browser.close()
                
        return hotels
