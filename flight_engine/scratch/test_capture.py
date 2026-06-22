import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.dto.flight_dto import SearchFlightRequest
from services.search_service import search_service
from infrastructure.registry import registry
from infrastructure.collectors.latam_collector import LatamCollector
from infrastructure.collectors.gol_collector import GolCollector
from infrastructure.collectors.azul_collector import AzulCollector
from infrastructure.collectors.copa_collector import CopaCollector
from infrastructure.collectors.avianca_collector import AviancaCollector
from infrastructure.collectors.tap_collector import TapCollector
from infrastructure.collectors.google_flights_collector import GoogleFlightsCollector
from infrastructure.collectors.kayak_collector import KayakCollector

# Registrando os coletores (como faríamos no startup do FastAPI)
registry.register(LatamCollector())
registry.register(GolCollector())
registry.register(AzulCollector())
registry.register(CopaCollector())
registry.register(AviancaCollector())
registry.register(TapCollector())
registry.register(GoogleFlightsCollector())
registry.register(KayakCollector())

async def run_test():
    try:
        # Simulando voo de IDA
        req_ida = SearchFlightRequest(
            origin="FOR", 
            destination="SCL",
            departure_date="2026-11-22",
            adults=1,
            strategy="cheapest"
        )

        print(f"--- Simulando Busca de IDA: {req_ida.origin} -> {req_ida.destination} ({req_ida.departure_date}) ---")
        dep_ida = datetime.strptime(req_ida.departure_date, "%Y-%m-%d")
        all_ida = await search_service._fetch_from_all_collectors(req_ida.origin, req_ida.destination, dep_ida, req_ida.adults)
        voos_ida = search_service._apply_strategy(all_ida, req_ida.strategy)
        
        if not voos_ida:
            print("Nenhum voo encontrado na ida.")
        for v in voos_ida:
            print(f"[{v.airline}] Partida: {v.departure_date.strftime('%d/%m/%Y %H:%M')} | Original: {v.currency} {v.price:.2f} -> BRL Convertido: R$ {v.base_price_brl:.2f}")

        # Simulando voo de VOLTA
        req_volta = SearchFlightRequest(
            origin="SCL",
            destination="FOR",
            departure_date="2026-11-30",
            adults=1,
            strategy="cheapest"
        )

        print(f"\n--- Simulando Busca de VOLTA: {req_volta.origin} -> {req_volta.destination} ({req_volta.departure_date}) ---")
        dep_volta = datetime.strptime(req_volta.departure_date, "%Y-%m-%d")
        all_volta = await search_service._fetch_from_all_collectors(req_volta.origin, req_volta.destination, dep_volta, req_volta.adults)
        voos_volta = search_service._apply_strategy(all_volta, req_volta.strategy)

        if not voos_volta:
            print("Nenhum voo encontrado na volta.")
        for v in voos_volta:
            print(f"[{v.airline}] Partida: {v.departure_date.strftime('%d/%m/%Y %H:%M')} | Original: {v.currency} {v.price:.2f} -> BRL Convertido: R$ {v.base_price_brl:.2f}")

    except Exception as e:
        print(f"Erro durante a simulação: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
