import httpx
import json

print("=== Testando API de Hoteis ===\n")

# Teste 1: SAO sem bounds
r = httpx.get("http://127.0.0.1:8000/api/hotels?destination=SAO&checkin=2026-07-20&checkout=2026-07-24", timeout=10)
data = r.json()
print(f"SAO sem bounds: {r.status_code} | {len(data)} resultados")
if data:
    print(f"  Primeiro: {data[0]['name']} | city={data[0]['city']} | lat={data[0]['latitude']}, lon={data[0]['longitude']}")

# Teste 2: RIO
r = httpx.get("http://127.0.0.1:8000/api/hotels?destination=RIO&checkin=2026-07-20&checkout=2026-07-24", timeout=10)
data = r.json()
print(f"\nRIO sem bounds: {r.status_code} | {len(data)} resultados")
if data:
    print(f"  Primeiro: {data[0]['name']} | city={data[0]['city']}")

# Teste 3: GRU (Guarulhos)
r = httpx.get("http://127.0.0.1:8000/api/hotels?destination=GRU&checkin=2026-07-20&checkout=2026-07-24", timeout=10)
data = r.json()
print(f"\nGRU sem bounds: {r.status_code} | {len(data)} resultados")

# Teste 4: FOR
r = httpx.get("http://127.0.0.1:8000/api/hotels?destination=FOR&checkin=2026-07-20&checkout=2026-07-24", timeout=10)
data = r.json()
print(f"\nFOR sem bounds: {r.status_code} | {len(data)} resultados")

# Teste 5: SAO com bounds de São Paulo
bounds = json.dumps({"north": -23.45, "south": -23.65, "east": -46.55, "west": -46.75})
r = httpx.get(f"http://127.0.0.1:8000/api/hotels?destination=SAO&checkin=2026-07-20&checkout=2026-07-24&bounds={bounds}", timeout=10)
data = r.json()
print(f"\nSAO com bounds SP: {r.status_code} | {len(data)} resultados")
