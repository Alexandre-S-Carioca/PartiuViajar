import httpx
import logging
import urllib.parse
from core.config import settings

logger = logging.getLogger(__name__)

class ScrapestackClient:
    def __init__(self):
        self.api_key = settings.SCRAPESTACK_API_KEY
        self.base_url = "http://api.scrapestack.com/scrape"

    async def scrape_html(self, target_url: str, render_js: bool = True, premium_proxy: bool = False) -> str | None:
        """
        Faz uma requisição via Scrapestack para contornar bloqueios e (opcionalmente) renderizar JS.
        Retorna o HTML puro resultante.
        """
        if not self.api_key:
            logger.error("SCRAPESTACK_API_KEY não configurada. Falha no ScrapestackClient.")
            return None

        params = {
            "access_key": self.api_key,
            "url": target_url,
        }
        if render_js:
            params["render_js"] = 1
        if premium_proxy:
            params["premium_proxy"] = 1

        query_string = urllib.parse.urlencode(params)
        request_url = f"{self.base_url}?{query_string}"

        logger.info(f"[Scrapestack] Solicitando scrap para a URL: {target_url}")
        
        try:
            # Tempo de timeout deve ser alto pois renderizar JS + proxy pode demorar
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                
                # A API retorna o HTML no corpo da resposta
                return response.text
        except Exception as e:
            logger.error(f"[Scrapestack] Erro ao raspar URL {target_url}: {str(e)}")
            return None

scrapestack_client = ScrapestackClient()
