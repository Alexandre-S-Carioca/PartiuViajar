document.addEventListener("DOMContentLoaded", () => {
    // Auth & Global State
    let accessToken = "";
    let map = null;
    let markerClusterGroup = null;
    let heatmapLayer = null;
    let drawnItems = null;
    let drawControl = null;
    let activePolygon = null;
    let isHeatmapActive = false;

    // Search parameters
    let currentCity = "";
    let checkinDate = "";
    let checkoutDate = "";

    // Selection State
    let selectedOutboundFlight = null;
    let selectedInboundFlight = null;
    let selectedHotel = null;

    // Lists for filtering
    let allFlights = [];
    let allHotels = [];
    let activeFlightSort = "price";
    let activeLodgingType = "all";
    let favoriteIds = new Set();

    // DOM references
    const form = document.getElementById("search-form");
    const flightsListView = document.getElementById("flights-list-view");
    const accommodationsListView = document.getElementById("accommodations-list-view");
    const loader = document.getElementById("results-loader");
    const comboContainer = document.getElementById("smart-combo-container");
    const summaryBox = document.getElementById("travel-summary-box");

    // Clear form fields on reload
    if (form) {
        form.reset();
        document.getElementById("origin").value = "";
        document.getElementById("destination").value = "";
        document.getElementById("departure_date").value = "";
        document.getElementById("return_date").value = "";
    }

    // City-center coordinates (used to position the map — NOT airport coordinates)
    const CITY_COORDS = {
        // São Paulo
        "SAO": [-23.5505, -46.6333],
        "GRU": [-23.5505, -46.6333],
        "CGH": [-23.5505, -46.6333],
        "VCP": [-23.5505, -46.6333],
        // Rio de Janeiro
        "RIO": [-22.9068, -43.1729],
        "GIG": [-22.9068, -43.1729],
        "SDU": [-22.9068, -43.1729],
        // Fortaleza
        "FOR": [-3.7327, -38.5270],
        // Santiago
        "SCL": [-33.4489, -70.6693],
        // Brasília
        "BSB": [-15.7801, -47.9292],
        // Salvador
        "SSA": [-12.9714, -38.5014],
        // Belo Horizonte
        "CNF": [-19.9167, -43.9345],
        "PLU": [-19.9167, -43.9345],
        // Curitiba
        "CWB": [-25.4290, -49.2671],
        // Porto Alegre
        "POA": [-30.0277, -51.2287],
        // Recife
        "REC": [-8.0539, -34.8811],
        // Manaus
        "MAO": [-3.1019, -60.0250],
        // Belém
        "BEL": [-1.4558, -48.5044],
        // Natal
        "NAT": [-5.7945, -35.2110],
        // Maceió
        "MCZ": [-9.6658, -35.7350],
        // Florianópolis
        "FLN": [-27.5954, -48.5480],
        // Goiânia
        "GYN": [-16.6864, -49.2643],
        // Teresina
        "THE": [-5.0920, -42.8038],
        // João Pessoa
        "JPA": [-7.1195, -34.8450],
        // Buenos Aires
        "EZE": [-34.6037, -58.3816],
        "AEP": [-34.6037, -58.3816]
    };

    // Current search mode: 'roundtrip' | 'oneway' | 'hotel-only'
    let searchMode = 'roundtrip';

    // Maps individual airport codes to the canonical city code used in the accommodations DB.
    // e.g. GRU (Guarulhos) and CGH (Congonhas) both belong to SAO (São Paulo)
    const AIRPORT_TO_CITY = {
        "GRU": "SAO",
        "CGH": "SAO",
        "VCP": "SAO",
        "GIG": "RIO",
        "SDU": "RIO",
        "SSA": "SSA",
        "BSB": "BSB",
        "CWB": "CWB",
        "POA": "POA",
        "BEL": "BEL",
        "MCZ": "MCZ",
        "NAT": "NAT",
        "REC": "REC",
        "MAO": "MAO",
        "SCL": "SCL",
        "EZE": "BUE",
        "AEP": "BUE",
        "FOR": "FOR",
        "SAO": "SAO",
        "RIO": "RIO"
    };

    // Returns the canonical city code for hotel search from an airport code
    function getCityCode(iataCode) {
        return AIRPORT_TO_CITY[iataCode] || iataCode;
    }

    // Flag to suppress map 'moveend' triggered hotel refetch during initial search
    let suppressMapRefetch = false;

    // Initialize Auth Token
    async function authenticate() {
        const formData = new URLSearchParams();
        formData.append("username", "test");
        formData.append("password", "test");
        try {
            const res = await fetch("/api/v1/auth/token", { method: "POST", body: formData });
            if (res.ok) {
                const data = await res.json();
                accessToken = data.access_token;
            }
        } catch (e) {
            console.error("Erro ao autenticar", e);
        }
    }
    authenticate();

    // Fetch initial favorites to populate active states
    async function fetchFavorites() {
        try {
            const res = await fetch("/api/favorites");
            if (res.ok) {
                const data = await res.json();
                favoriteIds = new Set(data.map(f => f.item_id));
            }
        } catch (err) {
            console.error("Error fetching favorites:", err);
        }
    }
    fetchFavorites();

    // Initialize Leaflet Map
    function initMap() {
        if (map) return;
        
        // Default center: São Paulo
        const center = CITY_COORDS["SAO"];
        map = L.map('leaflet-map-widget', { zoomControl: true }).setView(center, 12);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        markerClusterGroup = L.markerClusterGroup({
            showCoverageOnHover: false,
            maxClusterRadius: 40
        });
        map.addLayer(markerClusterGroup);

        // Setup drawing toolbar (Leaflet Draw)
        drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);
        
        drawControl = new L.Control.Draw({
            draw: {
                polygon: {
                    allowIntersection: false,
                    showArea: true,
                    drawError: { color: '#e15b64', message: '<strong>Erro!<strong> Você não pode cruzar linhas.' },
                    shapeOptions: { color: '#3b82f6', fillOpacity: 0.1 }
                },
                rect: false, circle: false, circlemarker: false, marker: false, polyline: false
            },
            edit: { featureGroup: drawnItems, remove: true }
        });
        map.addControl(drawControl);

        // Polygon Created event handler
        map.on(L.Draw.Event.CREATED, (e) => {
            drawnItems.clearLayers();
            const layer = e.layer;
            drawnItems.addLayer(layer);
            
            const latlngs = layer.getLatLngs()[0];
            activePolygon = latlngs.map(ll => [ll.lat, ll.lng]);
            
            // Trigger hotels filtering
            fetchHotelsAndRender();
        });

        // Polygon Removed event handler
        map.on(L.Draw.Event.DELETED, () => {
            activePolygon = null;
            fetchHotelsAndRender();
        });

        // Viewport move listener — suppressed during initial search transition
        map.on('moveend', () => {
            if (suppressMapRefetch) return;
            const syncCheck = document.getElementById("map-sync-move");
            if (syncCheck && syncCheck.checked && currentCity) {
                fetchHotelsAndRender();
            }
        });
    }

    initMap();

    // Autocomplete / Typeahead setup
    function setupAutocomplete(inputId, suggestionsId) {
        const input = document.getElementById(inputId);
        const dropdown = document.getElementById(suggestionsId);
        let items = [];
        let activeIndex = -1;
        let debounceTimer;

        async function fetchSuggestions(query) {
            try {
                let endpoint = `/api/v1/flights/airports/search?q=${encodeURIComponent(query)}`;
                // If searching for hotel destination and in hotel-only mode, use cities
                if (inputId === "destination" && searchMode === "hotel-only") {
                    endpoint = `/api/v1/flights/airports/cities/search?q=${encodeURIComponent(query)}`;
                }
                const response = await fetch(endpoint);
                if (!response.ok) throw new Error("API error");
                return await response.json();
            } catch (err) {
                console.error("Error fetching suggestions:", err);
                return [];
            }
        }

        function renderDropdown(suggestions) {
            items = suggestions;
            dropdown.innerHTML = "";
            activeIndex = -1;

            if (suggestions.length === 0) {
                dropdown.classList.add("hidden");
                return;
            }

            suggestions.forEach((item, index) => {
                const div = document.createElement("div");
                div.className = "suggestion-item";
                div.setAttribute("data-index", index);
                
                if (inputId === "destination" && searchMode === "hotel-only") {
                    div.innerHTML = `
                        <div class="suggestion-info">
                            <span class="suggestion-city-country">${item.city}, ${item.country}</span>
                        </div>
                    `;
                } else {
                    div.innerHTML = `
                        <div class="suggestion-info">
                            <span class="suggestion-city-country">${item.city}, ${item.country}</span>
                            <span class="suggestion-airport-name">${item.name}</span>
                        </div>
                        <span class="suggestion-code-badge">${item.code}</span>
                    `;
                }

                div.addEventListener("mousedown", (e) => {
                    e.preventDefault();
                    selectItem(index);
                });
                dropdown.appendChild(div);
            });

            dropdown.classList.remove("hidden");
        }

        function updateActiveItem() {
            const divs = dropdown.querySelectorAll(".suggestion-item");
            divs.forEach((div, index) => {
                if (index === activeIndex) {
                    div.classList.add("active");
                    div.scrollIntoView({ block: "nearest" });
                } else {
                    div.classList.remove("active");
                }
            });
        }

        function selectItem(index) {
            if (index >= 0 && index < items.length) {
                const selected = items[index];
                if (inputId === "destination" && searchMode === "hotel-only") {
                    input.value = `${selected.city}, ${selected.country}`;
                    input.setAttribute("data-code", selected.code);
                } else {
                    input.value = `${selected.city} (${selected.name}) - ${selected.code}`;
                }
                dropdown.classList.add("hidden");
                dropdown.innerHTML = "";
                activeIndex = -1;
            }
        }

        input.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            const query = input.value.trim();

            if (query.length < 1) {
                dropdown.classList.add("hidden");
                dropdown.innerHTML = "";
                return;
            }

            debounceTimer = setTimeout(async () => {
                const suggestions = await fetchSuggestions(query);
                renderDropdown(suggestions);
            }, 150);
        });

        input.addEventListener("keydown", (e) => {
            if (dropdown.classList.contains("hidden")) return;

            const divs = dropdown.querySelectorAll(".suggestion-item");
            if (divs.length === 0) return;

            if (e.key === "ArrowDown") {
                e.preventDefault();
                activeIndex = (activeIndex + 1) % divs.length;
                updateActiveItem();
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                activeIndex = (activeIndex - 1 + divs.length) % divs.length;
                updateActiveItem();
            } else if (e.key === "Enter") {
                if (activeIndex >= 0 && activeIndex < divs.length) {
                    e.preventDefault();
                    selectItem(activeIndex);
                }
            } else if (e.key === "Escape") {
                dropdown.classList.add("hidden");
                activeIndex = -1;
            }
        });

        document.addEventListener("click", (e) => {
            if (e.target !== input && !dropdown.contains(e.target)) {
                dropdown.classList.add("hidden");
                activeIndex = -1;
            }
        });

        input.addEventListener("focus", async () => {
            const query = input.value.trim();
            if (query && !query.includes(" - ")) {
                const suggestions = await fetchSuggestions(query);
                renderDropdown(suggestions);
            }
        });
    }

    setupAutocomplete("origin", "origin-suggestions");
    setupAutocomplete("destination", "destination-suggestions");

    // Extract IATA Code
    function getIataCode(value) {
        const match = value.match(/-\s*([A-Z]{3})\s*$/);
        return match ? match[1] : value.trim().toUpperCase();
    }

    // Perform Unified Search (Flights and Hotels)
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const dateVal = document.getElementById("departure_date").value;
        const returnDateVal = document.getElementById("return_date").value;
        const adultsVal = document.getElementById("adults").value;

        const destinationInput = document.getElementById("destination").value;
        const flightsListTitle = document.getElementById("flights-list-title");
        const hotelsListTitle = document.getElementById("hotels-list-title");
        
        const cityMatch = destinationInput.match(/^([^(]+)/);
        const cityName = cityMatch ? cityMatch[1].trim() : destinationInput;

        if (flightsListTitle) {
            flightsListTitle.innerText = "Passagens para " + cityName;
        }
        if (hotelsListTitle) {
            hotelsListTitle.innerText = "Hotéis em " + cityName;
        }

        const originVal = getIataCode(document.getElementById("origin").value);
        let destVal;
        let cityCode;
        if (searchMode === "hotel-only") {
            // For hotel-only, we just use the selected city string directly
            destVal = document.getElementById("destination").value;
            cityCode = document.getElementById("destination").getAttribute("data-code") || destVal; 
        } else {
            destVal = getIataCode(document.getElementById("destination").value);
            cityCode = getCityCode(destVal);
        }

        currentCity = cityCode;
        checkinDate = dateVal;
        // If no return date, default checkout to checkin + 1 day so hotels compute 1 night
        if (returnDateVal) {
            checkoutDate = returnDateVal;
        } else {
            const nextDay = new Date(dateVal);
            nextDay.setDate(nextDay.getDate() + 1);
            checkoutDate = nextDay.toISOString().split('T')[0];
        }

        // Save search history
        try {
            let history = JSON.parse(localStorage.getItem('partiuviajar_history') || '[]');
            let rawOrigin = document.getElementById("origin").value;
            let rawDest = document.getElementById("destination").value;
            let originName = rawOrigin ? rawOrigin.split('(')[0].trim() : '';
            let destName = rawDest ? rawDest.split('(')[0].trim() : 'Desconhecido';
            
            let text = searchMode === 'hotel-only' ? `Hotéis em ${destName}` : `${originName} → ${destName}`;
            let parts = dateVal.split('-');
            let dateStr = parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : dateVal;

            const entry = { mode: searchMode === 'hotel-only' ? 'hotels' : 'flights', text, date: dateStr, ts: Date.now() };
            
            if(!(history.length > 0 && history[0].text === entry.text && history[0].date === entry.date)) {
                history.unshift(entry);
                if(history.length > 5) history.pop();
                localStorage.setItem('partiuviajar_history', JSON.stringify(history));
            }
        } catch(err) { console.error("Error saving history:", err); }

        // Reset Selection state
        selectedOutboundFlight = null;
        selectedInboundFlight = null;
        selectedHotel = null;
        allFlights = [];
        allHotels = [];
        drawnItems.clearLayers();
        activePolygon = null;

        updateTravelSummary();

        // Show Loader
        loader.classList.remove("hidden");
        flightsListView.innerHTML = "";
        accommodationsListView.innerHTML = "";
        comboContainer.classList.add("hidden");

        // Set flags
        suppressMapRefetch = true;

        try {
            if (searchMode === "hotel-only") {
                await fetchHotelsAndRender(true);
            } else {
                const promises = [
                    fetchFlightsStream(originVal, destVal, dateVal, "IDA"),
                    fetchHotelsAndRender(true)
                ];
                if (returnDateVal && searchMode === 'roundtrip') {
                    promises.push(fetchFlightsStream(destVal, originVal, returnDateVal, "VOLTA"));
                }
                await Promise.all(promises);
            }
        } catch (err) {
            console.error("Search error", err);
        }

        // ===== CENTER MAP ON DESTINATION CITY =====
        // Always animate the map to the destination, using the city-center coords.
        // suppressMapRefetch prevents the moveend event from triggering a hotel refetch
        // before our explicit fetchHotelsAndRender() call below.
        const destCoords = CITY_COORDS[destVal] || CITY_COORDS[cityCode];
        if (destCoords && map) {
            map.flyTo(destCoords, 13, { animate: true, duration: 1.2 });
        }
        setTimeout(() => { suppressMapRefetch = false; }, 1400);

        loader.classList.add("hidden");
    });

    // Fetch flights stream via SSE
    async function fetchFlightsStream(fromCode, toCode, dateStr, tripType) {
        if (!accessToken) return;
        try {
            const url = `/api/flights/stream?origin=${fromCode}&destination=${toCode}&departure_date=${dateStr}&adults=1&strategy=cheapest`;
            const response = await fetch(url);
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop(); 
                
                for (const event of parts) {
                    if (event.startsWith("data: ")) {
                        const jsonStr = event.substring(6);
                        try {
                            const data = JSON.parse(jsonStr);
                            if (data.status === "success" && data.flights.length > 0) {
                                const processed = data.flights.map(f => ({
                                    ...f,
                                    tripType: tripType,
                                    collectorName: data.collector
                                }));
                                allFlights.push(...processed);
                                filterAndRenderFlights();
                            }
                        } catch (err) {
                            console.error("Parse error no chunk", jsonStr, err);
                        }
                    }
                }
            }
        } catch (err) {
            console.error(`SSE stream error for ${tripType}`, err);
        }
    }

    // Filter and display Flights
    function filterAndRenderFlights() {
        // Collect checked airlines
        const selectedAirlines = Array.from(document.querySelectorAll("input[name='airline-filter']:checked")).map(cb => cb.value.toLowerCase());
        const selectedStops = Array.from(document.querySelectorAll("input[name='stops-filter']:checked")).map(cb => parseInt(cb.value));
        const maxDepHour = parseInt(document.getElementById("filter-flight-hour-dep").value);
        const maxArrHour = parseInt(document.getElementById("filter-flight-hour-arr").value);

        let filtered = allFlights.filter(f => {
            // Airline filter
            if (selectedAirlines.length > 0 && !selectedAirlines.includes(f.airline.toLowerCase())) {
                const isMatched = selectedAirlines.some(sel => f.airline.toLowerCase().includes(sel));
                if (!isMatched) return false;
            }
            
            // Stops filter
            if (selectedStops.length > 0) {
                const matchStops = f.stops >= 2 ? selectedStops.includes(2) : selectedStops.includes(f.stops);
                if (!matchStops) return false;
            }

            // Hour filters
            const depHour = new Date(f.departure_date).getHours();
            if (depHour > maxDepHour) return false;

            const arrHour = new Date(f.arrival_date).getHours();
            if (arrHour > maxArrHour) return false;

            return true;
        });

        // Sorting
        filtered.sort((a, b) => {
            if (activeFlightSort === "price") {
                return parseFloat(a.base_price_brl) - parseFloat(b.base_price_brl);
            } else if (activeFlightSort === "duration") {
                return a.duration - b.duration;
            } else if (activeFlightSort === "stops") {
                return a.stops - b.stops;
            }
            return 0;
        });

        const countText = document.getElementById("flights-count-text");
        if (countText) {
            countText.textContent = `(${filtered.length} opções encontradas)`;
        }
        renderFlights(filtered);
        renderSmartCombo(filtered);
    }

    // Render individual flight cards
    function renderFlights(flights) {
        flightsListView.innerHTML = "";
        
        if (flights.length === 0) {
            flightsListView.innerHTML = `<div class="no-results">Nenhum voo atende aos filtros aplicados.</div>`;
            return;
        }

        flights.forEach(f => {
            const card = document.createElement("div");
            card.className = "flight-card";
            
            // Check if selected
            const isSel = (f.tripType === "IDA" && selectedOutboundFlight?.id === f.id) ||
                          (f.tripType === "VOLTA" && selectedInboundFlight?.id === f.id);
            if (isSel) card.classList.add("selected");

            const priceStr = parseFloat(f.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
            const depTime = new Date(f.departure_date).toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit' });
            const arrTime = new Date(f.arrival_date).toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit' });
            
            const hours = Math.floor(f.duration / 60);
            const mins = f.duration % 60;
            const durationStr = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;

            // Style airline logo
            let logoHTML = "";
            const airlineLower = f.airline.toLowerCase();
            if (airlineLower.includes("latam")) {
                logoHTML = `<span class="airline-name-text" style="color: #6d28d9; font-weight: 800; font-family: 'Outfit'; letter-spacing: -1px; display: flex; align-items: center; gap: 4px;"><span style="color: #e11d48; font-style: normal;">➔</span>LATAM</span>`;
            } else if (airlineLower.includes("gol")) {
                logoHTML = `<span class="airline-name-text" style="color: #ea580c; font-weight: 800; font-family: 'Outfit'; font-style: italic;">GOL</span>`;
            } else if (airlineLower.includes("azul")) {
                logoHTML = `<span class="airline-name-text" style="color: #1e3a8a; font-weight: 800; font-family: 'Outfit'; display: flex; align-items: center; gap: 2px;">Azul<span style="color: #3b82f6; font-size: 0.8rem;">✈</span></span>`;
            } else {
                logoHTML = `<span class="airline-name-text" style="color: #475569; font-weight: 800; font-family: 'Outfit';">${f.airline}</span>`;
            }

            card.innerHTML = `
                <div class="flight-airline-col">
                    <div class="airline-logo-box">
                        ${logoHTML}
                    </div>
                </div>
                <div class="flight-time-block">
                    <div class="time-box">
                        <span class="time-val">${depTime}</span>
                        <span class="airport-code">${f.origin}</span>
                    </div>
                    <div class="flight-timeline-path">
                        <span class="timeline-duration">${durationStr}</span>
                        <div class="timeline-line">
                            <span class="timeline-plane-dot"></span>
                        </div>
                        <span class="timeline-stops ${f.stops === 0 ? 'direct' : ''}">${f.stops === 0 ? 'Direto' : f.stops === 1 ? '1 escala' : `${f.stops} escalas`}</span>
                    </div>
                    <div class="time-box">
                        <span class="time-val">${arrTime}</span>
                        <span class="airport-code">${f.destination}</span>
                    </div>
                </div>
                <div class="flight-amenities-col">
                    <span class="flight-icon-badge" title="Bagagem de mão incluída">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" style="width: 14px; height: 14px;"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" /></svg>
                    </span>
                    <span class="flight-icon-badge" title="Assento incluído">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" style="width: 14px; height: 14px;"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
                    </span>
                </div>
                <div class="flight-pricing-col">
                    <span class="price-main">${priceStr}</span>
                    <span class="price-sub">Ida e volta</span>
                    <button class="btn-card-details">Ver detalhes</button>
                    <button type="button" class="history-chart-btn hidden" data-id="${f.id}"></button>
                </div>
            `;

            // Click Handler
            card.addEventListener("click", (e) => {
                if (e.target.classList.contains("history-chart-btn")) {
                    e.stopPropagation();
                    openPriceHistoryModal(f.id, f.airline, `${f.origin} ➔ ${f.destination}`);
                    return;
                }

                if (e.target.classList.contains("btn-card-details")) {
                    e.stopPropagation();
                    if (f.booking_url) {
                        window.open(f.booking_url, '_blank');
                    }
                    return;
                }
                
                if (f.tripType === "IDA") {
                    selectedOutboundFlight = selectedOutboundFlight?.id === f.id ? null : f;
                } else {
                    selectedInboundFlight = selectedInboundFlight?.id === f.id ? null : f;
                }
                filterAndRenderFlights();
                updateTravelSummary();
            });

            flightsListView.appendChild(card);
        });
    }

    // Render smart round-trip combined deals
    function renderSmartCombo(flights) {
        const idas = flights.filter(f => f.tripType === "IDA");
        const voltas = flights.filter(f => f.tripType === "VOLTA");

        if (idas.length === 0 || voltas.length === 0) {
            comboContainer.classList.add("hidden");
            return;
        }

        const cheapestIda = idas[0]; // Already sorted by active sort
        const cheapestVolta = voltas[0];

        if (cheapestIda && cheapestVolta) {
            const combinedPrice = parseFloat(cheapestIda.base_price_brl) + parseFloat(cheapestVolta.base_price_brl);
            const priceStr = combinedPrice.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

            comboContainer.innerHTML = `
                <div class="smart-combo-card glass">
                    <div class="combo-layout">
                        <div style="display:flex; flex-direction:column; gap:0.5rem; flex:1;">
                            <div style="font-size:0.85rem;">
                                <span style="font-size: 0.7em; background: rgba(59, 130, 246, 0.25); color: #60a5fa; padding: 2px 6px; border-radius: 4px; margin-right: 8px;">IDA</span>
                                <strong>${cheapestIda.airline}</strong> (${cheapestIda.origin} ➔ ${cheapestIda.destination}) - ${parseFloat(cheapestIda.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                            </div>
                            <div style="font-size:0.85rem; border-top:1px solid var(--card-border); padding-top:0.4rem;">
                                <span style="font-size: 0.7em; background: rgba(139, 92, 246, 0.25); color: #c084fc; padding: 2px 6px; border-radius: 4px; margin-right: 8px;">VOLTA</span>
                                <strong>${cheapestVolta.airline}</strong> (${cheapestVolta.origin} ➔ ${cheapestVolta.destination}) - ${parseFloat(cheapestVolta.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size: 0.7rem; color: var(--text-muted);">PREÇO COMBINADO</div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: var(--success);">${priceStr}</div>
                            <button id="btn-select-combo" style="font-size: 0.7rem; padding: 4px 8px; height: auto; margin-top: 0.3rem;">Selecionar Combo</button>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById("btn-select-combo").addEventListener("click", () => {
                selectedOutboundFlight = cheapestIda;
                selectedInboundFlight = cheapestVolta;
                filterAndRenderFlights();
                updateTravelSummary();
            });

            comboContainer.classList.remove("hidden");
        }
    }

    // Fetch Hotels and Render
    async function fetchHotelsAndRender(isNewSearch = false) {
        if (!currentCity) return;
        
        let url = `/api/hotels?destination=${currentCity}&checkin=${checkinDate}&checkout=${checkoutDate}`;

        // Accommodations price filter — only apply when slider is NOT at maximum
        const priceSlider = document.getElementById("filter-hotel-price");
        const maxPrice = parseFloat(priceSlider.value);
        const sliderMax = parseFloat(priceSlider.max);
        if (maxPrice < sliderMax) {
            url += `&max_price=${maxPrice}`;
        }

        const starCheckboxes = Array.from(document.querySelectorAll("input[name='stars-filter']:checked")).map(cb => cb.value);
        if (starCheckboxes.length > 0) {
            url += `&stars=${starCheckboxes.join(",")}`;
        }

        const amenityCheckboxes = Array.from(document.querySelectorAll(".amenity-checkbox:checked")).map(cb => cb.value);
        if (amenityCheckboxes.length > 0) {
            url += `&amenities=${encodeURIComponent(amenityCheckboxes.join(","))}`;
        }

        const typeFilters = [];
        if (activeLodgingType !== "all") {
            typeFilters.push(activeLodgingType);
        }
        if (typeFilters.length > 0) {
            url += `&types=${typeFilters.join(",")}`;
        }

        let boundsParam = "";
        const syncCheck = document.getElementById("map-sync-move");
        // If it's a new search, ignore bounds so we get hotels in the new city
        if (!isNewSearch && syncCheck && syncCheck.checked && !suppressMapRefetch) {
            const b = map.getBounds();
            const boundsObj = {
                north: b.getNorthEast().lat,
                east: b.getNorthEast().lng,
                south: b.getSouthWest().lat,
                west: b.getSouthWest().lng
            };
            boundsParam = `&bounds=${encodeURIComponent(JSON.stringify(boundsObj))}`;
        }
        url += boundsParam;

        // Polygon area filter
        if (activePolygon) {
            url += `&polygon=${encodeURIComponent(JSON.stringify(activePolygon))}`;
        }

        try {
            const res = await fetch(url);
            if (res.ok) {
                allHotels = await res.json();
                
                const countText = document.getElementById("hotels-count-text");
                if (countText) {
                    countText.textContent = `(${allHotels.length} opções encontradas)`;
                }
                
                sortAndRenderHotels();
            }
        } catch (err) {
            console.error("Error fetching hotels:", err);
        }
    }

    // Render accommodations cards list
    function renderHotels() {
        accommodationsListView.innerHTML = "";
        
        if (allHotels.length === 0) {
            accommodationsListView.innerHTML = `<div class="no-results">Nenhuma hospedagem encontrada na região. Mova o mapa ou altere os filtros.</div>`;
            return;
        }

        allHotels.forEach(acc => {
            const card = document.createElement("div");
            card.className = "lodging-card";
            
            if (selectedHotel?.id === acc.id) {
                card.classList.add("selected");
            }

            const starsStr = "★".repeat(acc.stars);
            const priceNight = parseFloat(acc.price_per_night).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
            const priceTotal = parseFloat(acc.price_total).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
            const isFav = favoriteIds.has(acc.id);

            // Amenities pills
            const amenitiesHTML = acc.amenities.slice(0, 5).map(a => `<span class="lodging-amenity-pill">${a}</span>`).join("");

            let ratingText = "Bom";
            if (acc.rating >= 9.0) ratingText = "Excelente";
            else if (acc.rating >= 8.5) ratingText = "Muito bom";
            else if (acc.rating >= 8.0) ratingText = "Bom";

            card.innerHTML = `
                <div class="lodging-image-wrapper">
                    <img src="${acc.photo_url}" class="lodging-img" alt="${acc.name}" onerror="this.src='https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=180&h=120&q=80'">
                </div>
                <div class="lodging-content">
                    <div class="lodging-title-row">
                        <span class="lodging-title">${acc.name}</span>
                    </div>
                    <div class="lodging-rating-reviews">
                        <span class="stars-gold">${starsStr}</span>
                        <span class="lodging-score">${acc.rating.toFixed(1)}</span>
                        <span class="lodging-reviews">${ratingText} (${acc.reviews_count} avaliações)</span>
                    </div>
                    <div class="lodging-center-dist">
                        ${acc.type.charAt(0).toUpperCase() + acc.type.slice(1)} - ${acc.distance_center.toFixed(1)} km do centro
                    </div>
                    <div class="lodging-amenities-row">
                        ${amenitiesHTML}
                    </div>
                </div>
                <div class="lodging-price-column">
                    <div>
                        <div class="lodging-price-night">${priceNight}<small>/noite</small></div>
                        <div class="lodging-price-total">Total: ${priceTotal}</div>
                        <div class="lodging-price-total-sub">${acc.nights || 4} diárias</div>
                    </div>
                    <div class="lodging-actions-row">
                        <button class="lodging-fav-btn ${isFav ? 'active' : ''}" data-id="${acc.id}">
                            ${isFav ? '❤️' : '🤍'}
                        </button>
                        <button class="lodging-details-btn">Ver detalhes</button>
                    </div>
                </div>
            `;

            // Click handler for Card selection
            card.addEventListener("click", (e) => {
                if (e.target.closest(".lodging-fav-btn") || e.target.classList.contains("lodging-details-btn")) {
                    return; // Skip selection on action buttons
                }
                selectedHotel = selectedHotel?.id === acc.id ? null : acc;
                renderHotels();
                updateTravelSummary();
            });

            // Details Button click
            card.querySelector(".lodging-details-btn").addEventListener("click", (e) => {
                e.stopPropagation();
                const hotelUrl = `https://www.booking.com/searchresults.pt-br.html?ss=${encodeURIComponent(acc.name + " " + acc.city)}&checkin=${checkinDate}&checkout=${checkoutDate}`;
                window.open(hotelUrl, '_blank');
            });

            // Toggle favorite button
            card.querySelector(".lodging-fav-btn").addEventListener("click", async (e) => {
                e.stopPropagation();
                await toggleFavoriteItem("accommodation", acc.id, acc);
                renderHotels();
            });

            accommodationsListView.appendChild(card);
        });
    }

    function sortAndRenderHotels() {
        const sortVal = document.getElementById("hotel-sort-select")?.value || "rating";
        allHotels.sort((a, b) => {
            if (sortVal === "rating") {
                return b.rating - a.rating;
            } else if (sortVal === "price_asc") {
                return parseFloat(a.price_per_night) - parseFloat(b.price_per_night);
            } else if (sortVal === "price_desc") {
                return parseFloat(b.price_per_night) - parseFloat(a.price_per_night);
            }
            return 0;
        });
        renderHotels();
        updateMapMarkers();
    }

    // Toggle favorite item in backend
    async function toggleFavoriteItem(type, id, details) {
        try {
            const res = await fetch("/api/favorites", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ item_type: type, item_id: id, details: details })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.status === "added") {
                    favoriteIds.add(id);
                } else {
                    favoriteIds.delete(id);
                }
            }
        } catch (err) {
            console.error("Error toggling favorite:", err);
        }
    }

    // Update map markers pin icons & heatmap
    async function updateMapMarkers() {
        if (!map || !markerClusterGroup) return;

        // Clear existing markers
        markerClusterGroup.clearLayers();
        if (heatmapLayer) {
            map.removeLayer(heatmapLayer);
            heatmapLayer = null;
        }

        const showHotels = document.getElementById("show-map-hotel").checked;
        const showPousadas = document.getElementById("show-map-pousada").checked;
        const showHostels = document.getElementById("show-map-hostel").checked;
        const showResorts = document.getElementById("show-map-resort").checked;

        const heatmapPoints = [];

        allHotels.forEach(acc => {
            // Check visibility checks
            if (acc.type === "hotel" && !showHotels) return;
            if (acc.type === "pousada" && !showPousadas) return;
            if (acc.type === "hostel" && !showHostels) return;
            if (acc.type === "resort" && !showResorts) return;

            const price = parseFloat(acc.price_per_night);
            
            let color = "green";
            if (price <= 150) color = "green";
            else if (price <= 250) color = "yellow";
            else if (price <= 400) color = "orange";
            else color = "red";

            // Push to heatmap points
            heatmapPoints.push([acc.latitude, acc.longitude, price]);

            // Custom Price Speech-bubble icon
            const priceLabel = `R$ ${Math.round(price)}`;
            const icon = L.divIcon({
                className: 'marker-price-bubble',
                html: `<div class="marker-pin pin-${color}">${priceLabel}</div>`,
                iconSize: [60, 25],
                iconAnchor: [30, 25]
            });

            const marker = L.marker([acc.latitude, acc.longitude], { icon: icon });

            // Popup layout
            const popupHTML = `
                <div class="map-popup-card">
                    <img src="${acc.photo_url}" class="map-popup-img" alt="${acc.name}" onerror="this.src='https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=200&h=90&q=80'">
                    <div class="map-popup-info-wrap">
                        <div class="map-popup-name">${acc.name}</div>
                        <div class="map-popup-rating">★ ${acc.rating.toFixed(1)} (${acc.stars} estrelas)</div>
                        <div style="font-size:0.7rem; color:#64748b">A ${acc.distance_center.toFixed(1)} km do centro</div>
                        <div class="map-popup-price">R$ ${Math.round(price)}/noite</div>
                        <button class="map-popup-select-btn" onclick="window.selectHotelFromMap('${acc.id}')">Ver detalhes</button>
                    </div>
                </div>
            `;

            marker.bindPopup(popupHTML);
            markerClusterGroup.addLayer(marker);
        });

        // Initialize Heatmap layer if active
        if (isHeatmapActive && heatmapPoints.length > 0) {
            heatmapLayer = L.heatLayer(heatmapPoints, {
                radius: 40,
                blur: 15,
                maxZoom: 14,
                gradient: { 0.4: 'blue', 0.65: 'lime', 1: 'red' }
            }).addTo(map);
        }
    }

    // Global selector callback for map popups
    window.selectHotelFromMap = (id) => {
        const found = allHotels.find(h => h.id === id);
        if (found) {
            selectedHotel = found;
            renderHotels();
            updateTravelSummary();
            map.closePopup();
        }
    };

    // Update Travel Summary Panel values
    function updateTravelSummary() {
        const summaryFlightPrice = document.getElementById("summary-flight-price");
        if (!summaryFlightPrice) return; // Safely exit if summary box is removed
        
        const summaryHotelPrice = document.getElementById("summary-hotel-price");
        const summaryNightsCount = document.getElementById("summary-nights-count");
        const summaryTotalPrice = document.getElementById("summary-total-price");
        const summaryInstallments = document.getElementById("summary-installments");

        let flightPriceVal = 0;
        if (selectedOutboundFlight) {
            flightPriceVal += parseFloat(selectedOutboundFlight.base_price_brl);
        }
        if (selectedInboundFlight) {
            flightPriceVal += parseFloat(selectedInboundFlight.base_price_brl);
        }

        let hotelPriceVal = 0;
        let nights = 0;
        if (selectedHotel) {
            hotelPriceVal = parseFloat(selectedHotel.price_total);
            nights = selectedHotel.nights;
        }

        const totalVal = flightPriceVal + hotelPriceVal;

        if (summaryFlightPrice) summaryFlightPrice.textContent = flightPriceVal.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        if (summaryHotelPrice) summaryHotelPrice.textContent = hotelPriceVal.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        if (summaryNightsCount) summaryNightsCount.textContent = nights;
        if (summaryTotalPrice) summaryTotalPrice.textContent = totalVal.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

        const monthlyVal = totalVal / 12;
        if (summaryInstallments) summaryInstallments.textContent = `Em até 12x de ${monthlyVal.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}`;
    }

    // Side filter listeners
    document.getElementById("btn-clear-filters").addEventListener("click", () => {
        document.querySelectorAll("input[name='airline-filter']").forEach(cb => cb.checked = true);
        document.querySelectorAll("input[name='stops-filter']").forEach(cb => cb.checked = true);
        document.getElementById("filter-flight-hour-dep").value = 23;
        document.getElementById("filter-flight-hour-arr").value = 23;
        document.getElementById("dep-hour-display").textContent = "23:59";
        document.getElementById("arr-hour-display").textContent = "23:59";
        document.getElementById("filter-hotel-price").value = 1500;
        document.getElementById("hotel-price-val").textContent = "R$ 1.500";
        document.querySelectorAll("input[name='stars-filter']").forEach(cb => cb.checked = true);
        document.querySelectorAll(".amenity-checkbox").forEach(cb => cb.checked = false);
        drawnItems.clearLayers();
        activePolygon = null;

        filterAndRenderFlights();
        fetchHotelsAndRender();
    });

    // Sub-filters inputs change listeners
    document.querySelectorAll("input[name='airline-filter'], input[name='stops-filter']").forEach(cb => {
        cb.addEventListener("change", filterAndRenderFlights);
    });

    document.getElementById("filter-flight-hour-dep").addEventListener("input", (e) => {
        document.getElementById("dep-hour-display").textContent = `${e.target.value.padStart(2, '0')}:59`;
        filterAndRenderFlights();
    });

    document.getElementById("filter-flight-hour-arr").addEventListener("input", (e) => {
        document.getElementById("arr-hour-display").textContent = `${e.target.value.padStart(2, '0')}:59`;
        filterAndRenderFlights();
    });

    document.getElementById("filter-hotel-price").addEventListener("input", (e) => {
        document.getElementById("hotel-price-val").textContent = `R$ ${parseInt(e.target.value).toLocaleString('pt-BR')}`;
        fetchHotelsAndRender();
    });

    document.querySelectorAll("input[name='stars-filter'], .amenity-checkbox").forEach(cb => {
        cb.addEventListener("change", fetchHotelsAndRender);
    });

    // Map checkboxes filtering
    document.querySelectorAll(".map-filters-inline input[type='checkbox']").forEach(cb => {
        cb.addEventListener("change", updateMapMarkers);
    });

    // ============================================================
    // SEARCH TABS (Ida e Volta / Só ida / Somente Hotel)
    // ============================================================
    const returnDateCard = document.getElementById("return-date-card");
    const originCard = document.getElementById("origin-card");
    const flightsSection = document.getElementById("section-flights-results");
    const flightsFiltersSection = document.getElementById("flights-filters-section");
    const hotelsFiltersSection = document.getElementById("hotels-filters-section");
    const filtersSeparator = document.getElementById("filters-separator");
    const searchTabsContainer = document.getElementById("search-tabs-container");

    // Add Main Nav Listeners
    document.getElementById("menu-flights")?.addEventListener("click", (e) => {
        e.preventDefault();
        document.getElementById("menu-flights").parentElement.classList.add("active");
        document.getElementById("menu-hotels").parentElement.classList.remove("active");
        searchTabsContainer.style.display = ""; // Show pill tabs
        setSearchMode('roundtrip');
    });

    document.getElementById("menu-hotels")?.addEventListener("click", (e) => {
        e.preventDefault();
        document.getElementById("menu-hotels").parentElement.classList.add("active");
        document.getElementById("menu-flights").parentElement.classList.remove("active");
        searchTabsContainer.style.display = "none"; // Hide pill tabs
        setSearchMode('hotel-only');
    });

    function setSearchMode(mode) {
        searchMode = mode;

        // Update active tab visual
        document.querySelectorAll(".search-tab-pill").forEach(b => b.classList.remove("active"));
        if (mode === 'roundtrip') {
            document.getElementById("tab-roundtrip")?.classList.add("active");
        } else if (mode === 'oneway') {
            document.getElementById("tab-oneway")?.classList.add("active");
        } else if (mode === 'hotel-only') {
            document.getElementById("tab-hotel")?.classList.add("active");
        }

        // Show/hide return date field
        if (returnDateCard) {
            // For roundtrip or hotel-only, show the return/check-out date field.
            returnDateCard.style.display = (mode === 'roundtrip' || mode === 'hotel-only') ? '' : 'none';
        }

        // Origin field visibility
        if (originCard) {
            const originInput = document.getElementById("origin");
            const swapBtnEl = document.getElementById("btn-swap-locations");
            
            if (mode === 'hotel-only') {
                originCard.style.display = 'none';
                if (originInput) originInput.removeAttribute('required');
                if (swapBtnEl) swapBtnEl.style.display = 'none';
            } else {
                originCard.style.display = '';
                if (originInput) originInput.setAttribute('required', 'required');
                if (swapBtnEl) swapBtnEl.style.display = '';
            }
        }

        // Dynamically update labels
        const lblDep = document.querySelector('label[for="departure_date"]');
        const lblRet = document.querySelector('label[for="return_date"]');
        const lblPax = document.querySelector('label[for="adults"]');

        if (mode === 'hotel-only') {
            if (lblDep) lblDep.textContent = "Check-in";
            if (lblRet) lblRet.textContent = "Check-out";
            if (lblPax) lblPax.textContent = "Hóspedes";
        } else {
            if (lblDep) lblDep.textContent = "Ida";
            if (lblRet) lblRet.textContent = "Volta";
            if (lblPax) lblPax.textContent = "Passageiros";
        }

        // Show/hide flights results section
        if (flightsSection) {
            flightsSection.style.display = (mode === 'hotel-only') ? 'none' : '';
        }

        // Handle Filters Visibility
        if (mode === 'hotel-only') {
            if (flightsFiltersSection) flightsFiltersSection.style.display = 'none';
            if (hotelsFiltersSection) hotelsFiltersSection.style.display = '';
            if (filtersSeparator) filtersSeparator.style.display = 'none';
        } else {
            if (flightsFiltersSection) flightsFiltersSection.style.display = '';
            if (hotelsFiltersSection) hotelsFiltersSection.style.display = 'none';
            if (filtersSeparator) filtersSeparator.style.display = 'none';
        }

        // Update search button label
        const searchBtn = document.getElementById("search-btn");
        if (searchBtn) {
            if (mode === 'hotel-only') {
                searchBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.2" stroke="currentColor" class="search-btn-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg>
                    Buscar hoteis`;
            } else {
                searchBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.2" stroke="currentColor" class="search-btn-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.637 10.637z" /></svg>
                    Buscar passagem`;
            }
        }
    }

    document.getElementById("tab-roundtrip")?.addEventListener("click", () => setSearchMode('roundtrip'));
    document.getElementById("tab-oneway")?.addEventListener("click", () => setSearchMode('oneway'));

    // Initialize default tab state
    setSearchMode('roundtrip');

    // Sort tabs listeners (hidden buttons kept for backward compat with filterAndRenderFlights)
    document.querySelectorAll(".sort-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".sort-tab").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeFlightSort = btn.getAttribute("data-sort");
            filterAndRenderFlights();
        });
    });

    // Lodging type tabs listeners
    document.querySelectorAll(".type-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".type-tab").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeLodgingType = btn.getAttribute("data-type");
            fetchHotelsAndRender();
        });
    });

    // Fullscreen Expand Map Toggle
    const expandMapBtn = document.getElementById("btn-expand-map");
    expandMapBtn.addEventListener("click", () => {
        const mapCol = document.querySelector(".map-column");
        mapCol.classList.toggle("expanded");
        if (mapCol.classList.contains("expanded")) {
            expandMapBtn.textContent = "✕ Fechar Mapa";
        } else {
            expandMapBtn.textContent = "⛶ Expandir Mapa";
        }
        setTimeout(() => {
            if (map) map.invalidateSize();
        }, 300);
    });

    // Heatmap Toggle
    const toggleHeatmapBtn = document.getElementById("btn-toggle-heatmap");
    toggleHeatmapBtn.addEventListener("click", () => {
        isHeatmapActive = !isHeatmapActive;
        toggleHeatmapBtn.classList.toggle("active");
        updateMapMarkers();
    });

    // Dark/Light Theme toggling
    document.getElementById("theme-toggle").addEventListener("click", () => {
        document.body.classList.toggle("light-mode");
    });

    // Swap locations click handler
    const swapBtn = document.getElementById("btn-swap-locations");
    if (swapBtn) {
        swapBtn.addEventListener("click", () => {
            const originInput = document.getElementById("origin");
            const destInput = document.getElementById("destination");
            const temp = originInput.value;
            originInput.value = destInput.value;
            destInput.value = temp;
        });
    }

    // Hotel sorting dropdown select listener
    const hotelSortSelect = document.getElementById("hotel-sort-select");
    if (hotelSortSelect) {
        hotelSortSelect.addEventListener("change", () => {
            sortAndRenderHotels();
        });
    }

    // Flight sorting dropdown select listener
    const flightSortSelect = document.getElementById("flight-sort-select");
    if (flightSortSelect) {
        flightSortSelect.addEventListener("change", (e) => {
            activeFlightSort = e.target.value;
            filterAndRenderFlights();
        });
    }

    // Modal: Search History & Favorites Handler
    const historyFavModal = document.getElementById("history-favorites-modal");
    const closeHistFavBtn = document.getElementById("close-history-fav-modal");

    document.getElementById("menu-alerts-history").addEventListener("click", (e) => {
        e.preventDefault();
        openHistoryFavoritesModal("history");
    });

    document.getElementById("menu-favorites").addEventListener("click", (e) => {
        e.preventDefault();
        openHistoryFavoritesModal("favorites");
    });

    closeHistFavBtn.addEventListener("click", () => {
        historyFavModal.classList.add("hidden");
    });

    async function openHistoryFavoritesModal(activeTab) {
        historyFavModal.classList.remove("hidden");
        historyFavModal.classList.add("show");
        
        const tabHist = document.getElementById("tab-show-history");
        const tabFav = document.getElementById("tab-show-favorites");

        if (activeTab === "history") {
            tabHist.classList.add("active");
            tabFav.classList.remove("active");
            await loadHistoryModalContent();
        } else {
            tabFav.classList.add("active");
            tabHist.classList.remove("active");
            await loadFavoritesModalContent();
        }

        tabHist.onclick = () => openHistoryFavoritesModal("history");
        tabFav.onclick = () => openHistoryFavoritesModal("favorites");
    }

    async function loadHistoryModalContent() {
        const body = document.getElementById("modal-list-content");
        body.innerHTML = "<div class='no-results'>Carregando histórico...</div>";
        try {
            const res = await fetch("/api/search-history");
            if (res.ok) {
                const data = await res.json();
                body.innerHTML = "";
                if (data.length === 0) {
                    body.innerHTML = "<div class='no-results'>Nenhuma busca no histórico.</div>";
                    return;
                }
                data.forEach(h => {
                    const card = document.createElement("div");
                    card.className = "history-item-card";
                    card.innerHTML = `
                        <div class="history-info">
                            <div class="history-title">${h.origin} ➔ ${h.destination}</div>
                            <div class="history-dates">Ida: ${h.departure_date} ${h.return_date ? `| Volta: ${h.return_date}` : ''} (${h.adults} passageiros)</div>
                        </div>
                        <button class="history-load-btn" data-origin="${h.origin}" data-dest="${h.destination}" data-dep="${h.departure_date}" data-ret="${h.return_date || ''}" data-adults="${h.adults}">Buscar</button>
                    `;
                    card.querySelector(".history-load-btn").onclick = (e) => {
                        e.stopPropagation();
                        // Load search values back to form
                        document.getElementById("origin").value = h.origin;
                        document.getElementById("destination").value = h.destination;
                        document.getElementById("departure_date").value = h.departure_date;
                        document.getElementById("return_date").value = h.return_date || "";
                        document.getElementById("adults").value = h.adults;
                        historyFavModal.classList.add("hidden");
                        form.dispatchEvent(new Event("submit"));
                    };
                    body.appendChild(card);
                });
            }
        } catch (err) {
            body.innerHTML = "<div class='no-results'>Erro ao carregar histórico.</div>";
        }
    }

    async function loadFavoritesModalContent() {
        const body = document.getElementById("modal-list-content");
        body.innerHTML = "<div class='no-results'>Carregando favoritos...</div>";
        try {
            const res = await fetch("/api/favorites");
            if (res.ok) {
                const data = await res.json();
                body.innerHTML = "";
                if (data.length === 0) {
                    body.innerHTML = "<div class='no-results'>Você não possui favoritos salvos.</div>";
                    return;
                }
                data.forEach(fav => {
                    const card = document.createElement("div");
                    card.className = "favorite-item-card";
                    card.innerHTML = `
                        <div class="fav-info">
                            <div class="fav-title">${fav.details.name || fav.details.airline || "Item Favorito"}</div>
                            <div class="fav-meta">${fav.item_type.toUpperCase()} | Preço por noite/voo: R$ ${parseFloat(fav.details.price_per_night || fav.details.base_price_brl).toFixed(2)}</div>
                        </div>
                        <button class="fav-load-btn" style="background:var(--danger)">Remover</button>
                    `;
                    card.querySelector(".fav-load-btn").onclick = async (e) => {
                        e.stopPropagation();
                        await toggleFavoriteItem(fav.item_type, fav.item_id, fav.details);
                        loadFavoritesModalContent();
                    };
                    body.appendChild(card);
                });
            }
        } catch (err) {
            body.innerHTML = "<div class='no-results'>Erro ao carregar favoritos.</div>";
        }
    }

    // Modal: Price History Modal (ChartJS dynamic loading)
    var historyChartInstance = null;
    function loadChartJs() {
        return new Promise((resolve, reject) => {
            if (window.Chart) { resolve(); return; }
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/chart.js";
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Chart.js"));
            document.head.appendChild(script);
        });
    }

    async function openPriceHistoryModal(flightId, airline, routeName) {
        const modal = document.getElementById("history-modal");
        const title = document.getElementById("history-route-title");
        title.textContent = `${airline} | ${routeName}`;
        
        modal.classList.remove("hidden");
        modal.offsetWidth; // force reflow
        modal.classList.add("show");

        try {
            await loadChartJs();
            const res = await fetch(`/api/v1/flights/price-history?flight_id=${flightId}`);
            if (!res.ok) throw new Error("API error");
            const data = await res.json();
            
            const labels = data.map(pt => pt.date);
            const prices = data.map(pt => pt.price);

            const ctx = document.getElementById("price-history-chart").getContext("2d");
            if (historyChartInstance) {
                historyChartInstance.destroy();
            }

            const gradient = ctx.createLinearGradient(0, 0, 0, 220);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

            historyChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Preço (R$)',
                        data: prices,
                        borderColor: '#3b82f6',
                        borderWidth: 2.5,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#3b82f6',
                        pointHoverRadius: 6,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        } catch (err) {
            console.error("Error rendering chart:", err);
        }
    }

    document.getElementById("close-history-modal").addEventListener("click", () => {
        const modal = document.getElementById("history-modal");
        modal.classList.remove("show");
        setTimeout(() => modal.classList.add("hidden"), 300);
    });

    // Modal Alert
    const alertModal = document.getElementById("alert-modal");
    document.getElementById("open-alert-btn").addEventListener("click", () => {
        let origin = document.getElementById("origin").value.trim();
        let dest = document.getElementById("destination").value.trim();
        const date = document.getElementById("departure_date").value;
        if (!origin || !dest || !date) {
            alert("Preencha Origem, Destino e Data de Ida para poder criar um alerta de preço.");
            return;
        }
        alertModal.classList.remove("hidden");
        alertModal.offsetWidth;
        alertModal.classList.add("show");
    });

    document.getElementById("close-alert-modal").addEventListener("click", () => {
        alertModal.classList.remove("show");
        setTimeout(() => alertModal.classList.add("hidden"), 300);
    });

    document.getElementById("alert-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        
        let origin = getIataCode(document.getElementById("origin").value);
        let dest = getIataCode(document.getElementById("destination").value);
        const date = document.getElementById("departure_date").value;

        const email = document.getElementById("alert-email").value;
        const telegram = document.getElementById("alert-telegram").value;
        const targetPrice = parseFloat(document.getElementById("alert-price").value);

        try {
            const res = await fetch("/api/v1/flights/alerts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: email,
                    telegram_chat_id: telegram || null,
                    origin: origin,
                    destination: dest,
                    departure_date: date,
                    target_price: targetPrice
                })
            });
            if (res.ok) {
                alert("Alerta criado com sucesso!");
                alertModal.classList.remove("show");
                setTimeout(() => alertModal.classList.add("hidden"), 300);
            }
        } catch (err) {
            console.error(err);
        }
    });

    // Close modals on clicking backdrop
    window.addEventListener("click", (e) => {
        const listMod = document.getElementById("history-favorites-modal");
        const histMod = document.getElementById("history-modal");
        if (e.target === listMod) {
            listMod.classList.add("hidden");
        }
        if (e.target === histMod) {
            histMod.classList.remove("show");
            setTimeout(() => histMod.classList.add("hidden"), 300);
        }
        if (e.target === alertModal) {
            alertModal.classList.remove("show");
            setTimeout(() => alertModal.classList.add("hidden"), 300);
        }
    });

    // View Details / Save Search callbacks inside summary card
    document.getElementById("btn-view-trip-details").addEventListener("click", () => {
        if (!selectedOutboundFlight && !selectedHotel) {
            alert("Selecione pelo menos um voo ou hospedagem para ver os detalhes da viagem.");
            return;
        }
        let msg = "Detalhes da sua Viagem:\n\n";
        if (selectedOutboundFlight) {
            msg += `✈ Voo Ida: ${selectedOutboundFlight.airline} (${selectedOutboundFlight.origin} -> ${selectedOutboundFlight.destination}) - R$ ${selectedOutboundFlight.base_price_brl}\n`;
        }
        if (selectedInboundFlight) {
            msg += `✈ Voo Volta: ${selectedInboundFlight.airline} (${selectedInboundFlight.origin} -> ${selectedInboundFlight.destination}) - R$ ${selectedInboundFlight.base_price_brl}\n`;
        }
        if (selectedHotel) {
            msg += `🏨 Hospedagem: ${selectedHotel.name} (${selectedHotel.nights} noites) - R$ ${selectedHotel.price_total}\n`;
        }
        alert(msg);
    });

    document.getElementById("btn-save-search").addEventListener("click", () => {
        if (!currentCity) {
            alert("Realize uma busca para poder salvá-la.");
            return;
        }
        alert("Busca salva com sucesso! Você pode visualizá-la na aba 'Alertas & Histórico' no menu superior.");
    });
});
