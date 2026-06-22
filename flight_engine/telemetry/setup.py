from prometheus_client import Counter, Histogram

requests_total = Counter("requests_total", "Total requests")
cache_hits = Counter("cache_hits", "Total cache hits")
cache_misses = Counter("cache_misses", "Total cache misses")
search_errors_total = Counter("search_errors_total", "Total search errors")

search_duration_seconds = Histogram("search_duration_seconds", "Search duration in seconds")
collector_duration_seconds = Histogram("collector_duration_seconds", "Collector duration in seconds", ["collector"])

# Quantities tracked
flights_returned_total = Counter("flights_returned_total", "Total flights returned")
hotels_returned_total = Counter("hotels_returned_total", "Total hotels returned")
pousadas_returned_total = Counter("pousadas_returned_total", "Total pousadas returned")
hostels_returned_total = Counter("hostels_returned_total", "Total hostels returned")
resorts_returned_total = Counter("resorts_returned_total", "Total resorts returned")

def setup_telemetry(app):
    pass

