import httpx
import logging
from typing import List, Dict, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class GeoApiClient:
    def __init__(self):
        self.api_key = settings.GEO_API_KEY
        self.base_url = "https://api.apilayer.com/geo"

    async def search_cities(self, query: str) -> List[Dict]:
        """
        Busca cidades pelo nome parcial ou completo na Geo API.
        """
        if not self.api_key:
            logger.warning("GEO_API_KEY não configurada. Geo API desativada.")
            return []
            
        if not query or len(query) < 2:
            return []

        url = f"{self.base_url}/city/name/{query}"
        headers = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # A API pode retornar erro dentro de 200 ou lista
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "message" in data:
                        logger.warning(f"Geo API retornou mensagem: {data['message']}")
                        return []
                else:
                    logger.error(f"Geo API retornou status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Erro ao conectar com a Geo API (City): {str(e)}")
            
        return []

    async def get_country_info(self, query: str) -> Optional[Dict]:
        """
        Busca informações de um país para extração de moeda e region_blocs.
        """
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/country/name/{query}"
        headers = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
        except Exception as e:
            logger.error(f"Erro ao conectar com a Geo API (Country): {str(e)}")
            
        return None

geo_api_client = GeoApiClient()
