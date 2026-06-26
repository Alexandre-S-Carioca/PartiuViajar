import os
import re

dir_path = "c:/Users/alexa/Projetos/Buscador/flight_engine/infrastructure/collectors"

# Match exactly: async def fetch_flights(self, origin: str, destination: str, departure_date: datetime, adults: int) -> ...
# Or without -> ...
# Be careful with whitespace

for filename in os.listdir(dir_path):
    if filename.endswith(".py"):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find fetch_flights signature
        new_content = re.sub(
            r'async def fetch_flights\s*\(\s*self,\s*origin:\s*str,\s*destination:\s*str,\s*departure_date:\s*datetime,\s*adults:\s*int\s*\)',
            r'async def fetch_flights(\n        self, origin: str, destination: str, departure_date: datetime, adults: int, currency: str = "BRL"\n    )',
            content
        )
        
        # If it's a hotel collector, it doesn't have fetch_flights, it has fetch_hotels. Let's ignore it safely because regex won't match.

        if "curr=BRL" in new_content:
            new_content = new_content.replace("curr=BRL", "curr={currency}")
            
        if "google_flights_collector" in filename:
            # specifically for google flights scrapestack or playwright, fix the URL f-string if needed
            new_content = new_content.replace("curr={currency}", "curr={currency}") # Already inside f-string? 
            # Wait, the url is: url = f"https://...&curr=BRL"
            # Replacing curr=BRL with curr={currency} inside an f-string makes it dynamically use the variable!

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filename}")
