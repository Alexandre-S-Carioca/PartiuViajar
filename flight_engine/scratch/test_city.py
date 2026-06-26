import httpx
import asyncio
import json

async def test_city_search():
    api_key = "nHY3hL1sKM8IrjsBqo3rnPLXCPXS9aJ9"
    url = "https://api.apilayer.com/geo/city/name/canoa quebrada"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"apikey": api_key})
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_city_search())
