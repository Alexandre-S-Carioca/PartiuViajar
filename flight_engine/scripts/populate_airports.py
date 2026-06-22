"""
Script para popular o airport_service.py com todos os aeroportos do mundo.

Fonte: OpenFlights Airports Database (https://openflights.org/data)
       Arquivo: airports.dat (~7.000 aeroportos mundiais, atualizado regularmente)

Uso:
    python scripts/populate_airports.py

O script irá:
1. Baixar o airports.dat da OpenFlights (grátis, sem autenticação)
2. Parsear e filtrar aeroportos válidos com código IATA de 3 letras
3. Reescrever o arquivo services/airport_service.py com a lista completa

Referência dos campos do airports.dat (CSV sem header):
    0 - Airport ID
    1 - Name
    2 - City
    3 - Country
    4 - IATA code (3 letras) ou \\N se não tiver
    5 - ICAO code (4 letras) ou \\N se não tiver
    6 - Latitude
    7 - Longitude
    8 - Altitude (pés)
    9 - Timezone offset UTC
   10 - DST (Daylight Saving Time)
   11 - Tz database timezone
   12 - Type
   13 - Source
"""

import csv
import io
import sys
import os
import re
from pathlib import Path
from urllib.request import urlopen, Request

# ──────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────
AIRPORTS_DAT_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

# Tradução de país (inglês → português) — os mais frequentes
COUNTRY_PT: dict[str, str] = {
    "Brazil": "Brasil",
    "United States": "Estados Unidos",
    "Argentina": "Argentina",
    "Chile": "Chile",
    "Colombia": "Colômbia",
    "Peru": "Peru",
    "Bolivia": "Bolívia",
    "Paraguay": "Paraguai",
    "Uruguay": "Uruguai",
    "Venezuela": "Venezuela",
    "Ecuador": "Equador",
    "Panama": "Panamá",
    "Mexico": "México",
    "Canada": "Canadá",
    "France": "França",
    "Germany": "Alemanha",
    "Italy": "Itália",
    "Spain": "Espanha",
    "Portugal": "Portugal",
    "United Kingdom": "Reino Unido",
    "Netherlands": "Holanda",
    "Switzerland": "Suíça",
    "Austria": "Áustria",
    "Belgium": "Bélgica",
    "Sweden": "Suécia",
    "Norway": "Noruega",
    "Denmark": "Dinamarca",
    "Finland": "Finlândia",
    "Poland": "Polônia",
    "Czech Republic": "República Tcheca",
    "Hungary": "Hungria",
    "Romania": "Romênia",
    "Greece": "Grécia",
    "Turkey": "Turquia",
    "Russia": "Rússia",
    "Ukraine": "Ucrânia",
    "China": "China",
    "Japan": "Japão",
    "South Korea": "Coreia do Sul",
    "India": "Índia",
    "Australia": "Austrália",
    "New Zealand": "Nova Zelândia",
    "South Africa": "África do Sul",
    "Egypt": "Egito",
    "Morocco": "Marrocos",
    "Nigeria": "Nigéria",
    "Kenya": "Quênia",
    "United Arab Emirates": "Emirados Árabes Unidos",
    "Saudi Arabia": "Arábia Saudita",
    "Qatar": "Catar",
    "Israel": "Israel",
    "Thailand": "Tailândia",
    "Singapore": "Singapura",
    "Malaysia": "Malásia",
    "Indonesia": "Indonésia",
    "Philippines": "Filipinas",
    "Vietnam": "Vietnã",
    "Cuba": "Cuba",
    "Dominican Republic": "República Dominicana",
    "Costa Rica": "Costa Rica",
    "Guatemala": "Guatemala",
    "Honduras": "Honduras",
    "El Salvador": "El Salvador",
    "Nicaragua": "Nicarágua",
    "Jamaica": "Jamaica",
    "Haiti": "Haiti",
    "Trinidad and Tobago": "Trinidad e Tobago",
    "Barbados": "Barbados",
    "Bahamas": "Bahamas",
    "Belize": "Belize",
    "Guyana": "Guiana",
    "Suriname": "Suriname",
    "French Guiana": "Guiana Francesa",
    "Bolivia": "Bolívia",
    "Paraguay": "Paraguai",
    "Iceland": "Islândia",
    "Ireland": "Irlanda",
    "Croatia": "Croácia",
    "Serbia": "Sérvia",
    "Slovakia": "Eslováquia",
    "Slovenia": "Eslovênia",
    "Bulgaria": "Bulgária",
    "Lithuania": "Lituânia",
    "Latvia": "Letônia",
    "Estonia": "Estônia",
    "Albania": "Albânia",
    "North Macedonia": "Macedônia do Norte",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "Montenegro": "Montenegro",
    "Moldova": "Moldávia",
    "Belarus": "Bielorrússia",
    "Georgia": "Geórgia",
    "Armenia": "Armênia",
    "Azerbaijan": "Azerbaijão",
    "Kazakhstan": "Cazaquistão",
    "Uzbekistan": "Uzbequistão",
    "Pakistan": "Paquistão",
    "Bangladesh": "Bangladesh",
    "Sri Lanka": "Sri Lanka",
    "Nepal": "Nepal",
    "Myanmar": "Mianmar",
    "Cambodia": "Camboja",
    "Laos": "Laos",
    "Mongolia": "Mongólia",
    "Afghanistan": "Afeganistão",
    "Iraq": "Iraque",
    "Iran": "Irã",
    "Syria": "Síria",
    "Lebanon": "Líbano",
    "Jordan": "Jordânia",
    "Kuwait": "Kuwait",
    "Bahrain": "Bahrein",
    "Oman": "Omã",
    "Yemen": "Iêmen",
    "Libya": "Líbia",
    "Tunisia": "Tunísia",
    "Algeria": "Argélia",
    "Senegal": "Senegal",
    "Ghana": "Gana",
    "Ethiopia": "Etiópia",
    "Tanzania": "Tanzânia",
    "Uganda": "Uganda",
    "Mozambique": "Moçambique",
    "Angola": "Angola",
    "Zimbabwe": "Zimbábue",
    "Zambia": "Zâmbia",
    "Madagascar": "Madagascar",
    "Cameroon": "Camarões",
    "Ivory Coast": "Costa do Marfim",
    "Mali": "Mali",
    "Burkina Faso": "Burkina Faso",
    "Guinea": "Guiné",
    "Niger": "Níger",
    "Chad": "Chade",
    "Sudan": "Sudão",
    "Somalia": "Somália",
    "Eritrea": "Eritreia",
    "Djibouti": "Djibuti",
    "Rwanda": "Ruanda",
    "Burundi": "Burundi",
    "Congo (Kinshasa)": "Congo (RDC)",
    "Congo (Brazzaville)": "Congo (República)",
    "Gabon": "Gabão",
    "Namibia": "Namíbia",
    "Botswana": "Botsuana",
    "Lesotho": "Lesoto",
    "Swaziland": "Suazilândia",
    "Malawi": "Maláui",
    "Cape Verde": "Cabo Verde",
    "Fiji": "Fiji",
    "Papua New Guinea": "Papua Nova Guiné",
    "Solomon Islands": "Ilhas Salomão",
    "Vanuatu": "Vanuatu",
    "Samoa": "Samoa",
    "Tonga": "Tonga",
    "Maldives": "Maldivas",
    "Seychelles": "Seicheles",
    "Mauritius": "Maurício",
    "Reunion": "Reunião",
    "Hong Kong": "Hong Kong",
    "Macau": "Macau",
    "Taiwan": "Taiwan",
}


def translate_country(name: str) -> str:
    return COUNTRY_PT.get(name, name)


def download_airports() -> list[dict]:
    """Download and parse airports.dat from OpenFlights."""
    print(f"Baixando {AIRPORTS_DAT_URL} ...")
    req = Request(AIRPORTS_DAT_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="replace")

    print(f"Download completo. Tamanho: {len(content):,} bytes")

    airports = []
    reader = csv.reader(io.StringIO(content))
    for row in reader:
        if len(row) < 6:
            continue

        iata = row[4].strip().strip('"').upper()

        # Somente aeroportos com código IATA válido (3 letras)
        if not iata or iata == r"\N" or not re.match(r"^[A-Z]{3}$", iata):
            continue

        name = row[1].strip().strip('"')
        city = row[2].strip().strip('"')
        country = translate_country(row[3].strip().strip('"'))

        # Pular entradas claramente inválidas
        if not name or not city or not country:
            continue

        airports.append({
            "code": iata,
            "city": city,
            "name": name,
            "country": country,
        })

    print(f"Total de aeroportos com código IATA válido: {len(airports):,}")
    return airports


def generate_python_file(airports: list[dict], output_path: Path) -> None:
    """Generate the airport_service.py file with the full airport list."""

    # Sort by country then city for readability
    airports.sort(key=lambda a: (a["country"], a["city"], a["code"]))

    # Remove duplicates (same IATA code — keep first occurrence)
    seen_codes: set[str] = set()
    unique: list[dict] = []
    for ap in airports:
        if ap["code"] not in seen_codes:
            seen_codes.add(ap["code"])
            unique.append(ap)

    print(f"Aeroportos únicos (sem duplicatas): {len(unique):,}")

    # Build the Python list literal
    import json
    lines = []
    for ap in unique:
        # json.dumps will handle all escaping (quotes, newlines, etc)
        lines.append(f"    {json.dumps(ap, ensure_ascii=False)},")

    data_block = "\n".join(lines)

    file_content = f'''\
from typing import List, Dict
import unicodedata

# ============================================================
# COMPREHENSIVE GLOBAL AIRPORTS DATABASE
# Source: OpenFlights (https://openflights.org/data)
# Total airports: {len(unique):,}
# Last updated: via scripts/populate_airports.py
# ============================================================
AIRPORTS_DATA: List[Dict[str, str]] = [
{data_block}
]


def normalize_text(text: str) -> str:
    """Normalize text by removing accents and converting to lowercase."""
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKD', text)
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


class AirportService:
    def __init__(self):
        # Precompute normalized fields for fast searching
        self.airports = []
        for ap in AIRPORTS_DATA:
            self.airports.append({{
                "code": ap["code"],
                "city": ap["city"],
                "name": ap["name"],
                "country": ap["country"],
                # Precompiled searchable string
                "search_str": normalize_text(f"{{ap[\'code\']}} {{ap[\'city\']}} {{ap[\'name\']}} {{ap[\'country\']}}")
            }})

    def search(self, query: str, limit: int = 8) -> List[Dict[str, str]]:
        """Search airports by code, city, name, or country, ranking matches."""
        if not query:
            return self.airports[:limit]

        normalized_query = normalize_text(query.strip())

        matches = []
        for ap in self.airports:
            # 1. Exact match on airport code gets highest priority
            if ap["code"].lower() == normalized_query:
                score = 100
            # 2. Code prefix match gets high priority
            elif ap["code"].lower().startswith(normalized_query):
                score = 80
            # 3. City name prefix match gets priority
            elif normalize_text(ap["city"]).startswith(normalized_query):
                score = 60
            # 4. General match on code/city/name/country
            elif normalized_query in ap["search_str"]:
                score = 20
            else:
                continue

            matches.append((score, {{
                "code": ap["code"],
                "city": ap["city"],
                "name": ap["name"],
                "country": ap["country"],
                "display": f"{{ap[\'city\']}} ({{ap[\'name\']}}) - {{ap[\'code\']}}"
            }}))

        # Sort matches by score descending, then by city name alphabetically
        matches.sort(key=lambda x: (-x[0], x[1]["city"]))
        return [item[1] for item in matches[:limit]]


airport_service = AirportService()
'''

    output_path.write_text(file_content, encoding="utf-8")
    print(f"Arquivo gerado: {output_path}")
    print(f"Tamanho do arquivo: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    # Locate the project root (2 levels up from scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_path = project_root / "services" / "airport_service.py"

    if not output_path.parent.exists():
        print(f"ERRO: Diretório não encontrado: {output_path.parent}")
        sys.exit(1)

    airports = download_airports()

    if not airports:
        print("ERRO: Nenhum aeroporto foi carregado. Verifique a conexão com a internet.")
        sys.exit(1)

    # Backup original file
    backup_path = output_path.with_suffix(".py.backup")
    if output_path.exists():
        import shutil
        shutil.copy2(output_path, backup_path)
        print(f"Backup criado: {backup_path}")

    generate_python_file(airports, output_path)

    print("\n[OK] Concluido! Reinicie o servidor FastAPI para carregar os novos dados:")
    print("   (Ctrl+C no terminal do servidor, depois execute novamente: uvicorn main:app --reload)")


if __name__ == "__main__":
    main()
