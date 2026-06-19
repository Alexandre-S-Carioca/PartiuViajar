from typing import List, Dict
import unicodedata

# Comprehensive in-memory dataset of major domestic and international airports.
AIRPORTS_DATA: List[Dict[str, str]] = [
    {"code": "FOR", "city": "Fortaleza", "name": "Pinto Martins", "country": "Brasil"},
    {"code": "SCL", "city": "Santiago", "name": "Arturo Merino Benítez", "country": "Chile"},
    {"code": "GRU", "city": "São Paulo", "name": "Guarulhos", "country": "Brasil"},
    {"code": "CGH", "city": "São Paulo", "name": "Congonhas", "country": "Brasil"},
    {"code": "GIG", "city": "Rio de Janeiro", "name": "Galeão", "country": "Brasil"},
    {"code": "SDU", "city": "Rio de Janeiro", "name": "Santos Dumont", "country": "Brasil"},
    {"code": "BSB", "city": "Brasília", "name": "Presidente Juscelino Kubitschek", "country": "Brasil"},
    {"code": "MIA", "city": "Miami", "name": "Miami International", "country": "Estados Unidos"},
    {"code": "JFK", "city": "Nova York", "name": "John F. Kennedy", "country": "Estados Unidos"},
    {"code": "CDG", "city": "Paris", "name": "Charles de Gaulle", "country": "França"},
    {"code": "LHR", "city": "Londres", "name": "Heathrow", "country": "Reino Unido"},
    {"code": "MAD", "city": "Madrid", "name": "Barajas", "country": "Espanha"},
    {"code": "EZE", "city": "Buenos Aires", "name": "Ministro Pistarini (Ezeiza)", "country": "Argentina"},
    {"code": "AEP", "city": "Buenos Aires", "name": "Aeroparque Jorge Newbery", "country": "Argentina"},
    {"code": "VCP", "city": "Campinas", "name": "Viracopos", "country": "Brasil"},
    {"code": "CNF", "city": "Belo Horizonte", "name": "Confins (Tancredo Neves)", "country": "Brasil"},
    {"code": "POA", "city": "Porto Alegre", "name": "Salgado Filho", "country": "Brasil"},
    {"code": "CWB", "city": "Curitiba", "name": "Afonso Pena", "country": "Brasil"},
    {"code": "REC", "city": "Recife", "name": "Gilberto Freyre (Guararapes)", "country": "Brasil"},
    {"code": "SSA", "city": "Salvador", "name": "Deputado Luís Eduardo Magalhães", "country": "Brasil"},
    {"code": "FLN", "city": "Florianópolis", "name": "Hercílio Luz", "country": "Brasil"},
    {"code": "BEL", "city": "Belém", "name": "Val-de-Cans", "country": "Brasil"},
    {"code": "MAO", "city": "Manaus", "name": "Eduardo Gomes", "country": "Brasil"},
    {"code": "CGB", "city": "Cuiabá", "name": "Marechal Rondon", "country": "Brasil"},
    {"code": "GYN", "city": "Goiânia", "name": "Santa Genoveva", "country": "Brasil"},
    {"code": "NAT", "city": "Natal", "name": "Aluízio Alves", "country": "Brasil"},
    {"code": "MCZ", "city": "Maceió", "name": "Zumbi dos Palmares", "country": "Brasil"},
    {"code": "IGU", "city": "Foz do Iguaçu", "name": "Cataratas", "country": "Brasil"},
    {"code": "SLZ", "city": "São Luís", "name": "Marechal Cunha Machado", "country": "Brasil"},
    {"code": "LIM", "city": "Lima", "name": "Jorge Chávez", "country": "Peru"},
    {"code": "BOG", "city": "Bogotá", "name": "El Dorado", "country": "Colômbia"},
    {"code": "PTY", "city": "Cidade do Panamá", "name": "Tocumen", "country": "Panamá"},
    {"code": "MCO", "city": "Orlando", "name": "Orlando International", "country": "Estados Unidos"},
    {"code": "LAX", "city": "Los Angeles", "name": "Los Angeles International", "country": "Estados Unidos"},
    {"code": "MUC", "city": "Munique", "name": "Franz Josef Strauss", "country": "Alemanha"},
    {"code": "FCO", "city": "Roma", "name": "Fiumicino (Leonardo da Vinci)", "country": "Itália"},
    {"code": "LIS", "city": "Lisboa", "name": "Humberto Delgado", "country": "Portugal"},
    {"code": "ORY", "city": "Paris", "name": "Orly", "country": "França"},
    {"code": "AMS", "city": "Amsterdã", "name": "Schiphol", "country": "Holanda"},
    {"code": "DXB", "city": "Dubai", "name": "Dubai International", "country": "Emirados Árabes Unidos"},
    {"code": "VIX", "city": "Vitória", "name": "Eurico de Aguiar Salles", "country": "Brasil"},
    {"code": "NVT", "city": "Navegantes", "name": "Ministro Victor Konder", "country": "Brasil"},
    {"code": "JOI", "city": "Joinville", "name": "Lauro Carneiro de Loyola", "country": "Brasil"},
    {"code": "UDI", "city": "Uberlândia", "name": "César Bombonato", "country": "Brasil"},
    {"code": "RAO", "city": "Ribeirão Preto", "name": "Leite Lopes", "country": "Brasil"},
    {"code": "SJP", "city": "São José do Rio Preto", "name": "Eribelto Manoel Reino", "country": "Brasil"},
    {"code": "IZA", "city": "Juiz de Fora", "name": "Presidente Itamar Franco", "country": "Brasil"},
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
            self.airports.append({
                "code": ap["code"],
                "city": ap["city"],
                "name": ap["name"],
                "country": ap["country"],
                # Precompiled searchable string
                "search_str": normalize_text(f"{ap['code']} {ap['city']} {ap['name']} {ap['country']}")
            })

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

            matches.append((score, {
                "code": ap["code"],
                "city": ap["city"],
                "name": ap["name"],
                "country": ap["country"],
                "display": f"{ap['city']} ({ap['name']}) - {ap['code']}"
            }))

        # Sort matches by score descending, then by city name alphabetically
        matches.sort(key=lambda x: (-x[0], x[1]["city"]))
        return [item[1] for item in matches[:limit]]

airport_service = AirportService()
