import asyncio
import sys
sys.path.append('c:/Users/alexa/Projetos/Buscador/flight_engine')
from infrastructure.clients.aviationstack_client import aviationstack_client
import traceback
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    try:
        res = await aviationstack_client.get_live_flight_status('3U9619')
        print(res)
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
