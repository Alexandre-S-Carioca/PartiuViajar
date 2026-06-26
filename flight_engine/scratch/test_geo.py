import httpx
import asyncio

async def test_geo_api():
    print("Iniciando teste da APILayer Geo API...")
    
    api_key = "nHY3hL1sKM8IrjsBqo3rnPLXCPXS9aJ9" 
    
    url = "https://api.apilayer.com/geo/country/name/brazil"
    
    headers = {
        "apikey": api_key
    }
    
    print(f"Buscando informações do país 'brazil'...")
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        status = response.status_code
        print(f"Status Code: {status}")
        
        try:
            data = response.json()
            import json
            print("Resposta:\n", json.dumps(data, indent=2))
        except Exception as e:
            text = response.text
            print("Erro ao decodificar JSON. Resposta pura:")
            print(text)

if __name__ == "__main__":
    asyncio.run(test_geo_api())
