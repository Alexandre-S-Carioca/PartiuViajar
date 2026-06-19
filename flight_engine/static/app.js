document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("search-form");
    const grid = document.getElementById("flights-grid");
    const loader = document.getElementById("loader");

    // Clear form inputs on initial load (F5)
    if (form) {
        form.reset();
        document.getElementById("origin").value = "";
        document.getElementById("destination").value = "";
        document.getElementById("departure_date").value = "";
        document.getElementById("return_date").value = "";
    }

    let accessToken = "";

    // Auth mock token retrieval
    async function authenticate() {
        const formData = new URLSearchParams();
        formData.append("username", "test");
        formData.append("password", "test");

        try {
            const res = await fetch("/api/v1/auth/token", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            accessToken = data.access_token;
        } catch (e) {
            console.error("Erro ao autenticar", e);
        }
    }

    authenticate();

    // Global state for collected flights and filtering
    let allFlights = [];
    let discoveredAirlines = new Set();
    let selectedAirlines = new Set();
    let activeSort = "price";

    // DOM references for sidebar and filters
    const sidebar = document.getElementById("filters-sidebar");
    const filterStops = document.getElementById("filter-stops");
    const filterPrice = document.getElementById("filter-price");
    const priceLimitVal = document.getElementById("price-limit-val");
    const filterAirlinesList = document.getElementById("filter-airlines-list");
    const comboContainer = document.getElementById("smart-combo-container");

    // Clear and hide state before new search
    function resetSearchState() {
        allFlights = [];
        discoveredAirlines.clear();
        selectedAirlines.clear();
        grid.innerHTML = "";
        comboContainer.classList.add("hidden");
        comboContainer.innerHTML = "";
        sidebar.classList.add("hidden");
        
        // Reset filter inputs
        filterStops.value = "any";
        filterPrice.value = "10000";
        priceLimitVal.textContent = "R$ 10.000";
        filterAirlinesList.innerHTML = "";
    }

    // Set up filter input change listeners
    filterStops.addEventListener("change", applyFiltersAndRender);
    filterPrice.addEventListener("input", () => {
        const val = parseFloat(filterPrice.value);
        priceLimitVal.textContent = val.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
        applyFiltersAndRender();
    });

    // Sort buttons listeners
    document.querySelectorAll(".sort-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeSort = btn.getAttribute("data-sort");
            applyFiltersAndRender();
        });
    });

    // Populate airline checkboxes dynamically
    function updateAirlineFilters(flights) {
        let listChanged = false;
        flights.forEach(f => {
            if (f.airline && !discoveredAirlines.has(f.airline)) {
                discoveredAirlines.add(f.airline);
                listChanged = true;
            }
        });

        if (listChanged) {
            filterAirlinesList.innerHTML = "";
            discoveredAirlines.forEach(airline => {
                const label = document.createElement("label");
                label.innerHTML = `
                    <input type="checkbox" value="${airline}" ${selectedAirlines.has(airline) ? 'checked' : ''}>
                    ${airline}
                `;
                label.querySelector("input").addEventListener("change", (e) => {
                    if (e.target.checked) {
                        selectedAirlines.add(airline);
                    } else {
                        selectedAirlines.delete(airline);
                    }
                    applyFiltersAndRender();
                });
                filterAirlinesList.appendChild(label);
            });
        }
    }

    // Core filter/sort function
    function applyFiltersAndRender() {
        const maxStops = filterStops.value;
        const maxPrice = parseFloat(filterPrice.value);

        // Filter flights
        let filtered = allFlights.filter(f => {
            if (maxStops !== "any" && f.stops > parseInt(maxStops)) return false;
            if (parseFloat(f.base_price_brl) > maxPrice) return false;
            if (selectedAirlines.size > 0 && !selectedAirlines.has(f.airline)) return false;
            return true;
        });

        // Sort flights
        filtered.sort((a, b) => {
            if (activeSort === "price") {
                return parseFloat(a.base_price_brl) - parseFloat(b.base_price_brl);
            } else if (activeSort === "duration") {
                return parseInt(a.duration) - parseInt(b.duration);
            } else if (activeSort === "stops") {
                return parseInt(a.stops) - parseInt(b.stops);
            }
            return 0;
        });

        // Render flights grid
        grid.innerHTML = "";
        if (filtered.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 3rem;">Nenhum voo atende aos filtros aplicados.</div>`;
        } else {
            renderFlightsList(filtered);
        }

        // Render smart round-trip combined deals
        calculateSmartCombo();
    }

    // Render individual flight cards to DOM
    function renderFlightsList(flights) {
        flights.forEach((flight, index) => {
            const card = document.createElement("a");
            card.className = "flight-card glass";
            card.href = flight.booking_url || "#";
            card.target = "_blank";
            card.rel = "noopener noreferrer";
            card.style.animationDelay = `${index * 0.03}s`;

            const price = parseFloat(flight.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
            const dateObj = new Date(flight.departure_date);
            const dateStr = dateObj.toLocaleDateString("pt-BR", { day: '2-digit', month: '2-digit', hour: '2-digit', minute:'2-digit' });

            card.innerHTML = `
                <div class="card-header">
                    <span class="airline">
                        <span style="font-size: 0.7em; background: rgba(59, 130, 246, 0.2); padding: 2px 6px; border-radius: 4px; color: var(--primary); margin-right: 8px;">${flight.tripType}</span>
                        ${flight.airline || "Voo"} 
                        <small style="font-size:0.6em;color:var(--text-muted)">(${flight.collectorName})</small>
                    </span>
                    <span class="price">${price}</span>
                </div>
                <div class="card-body">
                    <div class="route">
                        <strong>${flight.origin}</strong> ➔ <strong>${flight.destination}</strong>
                        <div style="margin-top: 0.5rem">${dateStr}</div>
                    </div>
                    <div class="details" style="text-align: right;">
                        <div>Duração: ${flight.duration} min</div>
                        <div>Escalas: ${flight.stops}</div>
                        <div>${flight.cabin_class}</div>
                        <button type="button" class="history-chart-btn" data-id="${flight.id}">
                            📈 Histórico
                        </button>
                    </div>
                </div>
            `;

            // Setup price history button
            const chartBtn = card.querySelector(".history-chart-btn");
            chartBtn.addEventListener("click", (event) => {
                event.preventDefault();
                event.stopPropagation();
                openHistoryModal(flight.id, flight.airline, `${flight.origin} ➔ ${flight.destination}`);
            });

            grid.appendChild(card);
        });
    }

    // Smart combined deals builder (IDA + VOLTA cheap combinations)
    function calculateSmartCombo() {
        const idas = allFlights.filter(f => f.tripType === "IDA");
        const voltas = allFlights.filter(f => f.tripType === "VOLTA");

        if (idas.length === 0 || voltas.length === 0) {
            comboContainer.classList.add("hidden");
            return;
        }

        // Sort by price
        const cheapestIda = [...idas].sort((a,b) => parseFloat(a.base_price_brl) - parseFloat(b.base_price_brl))[0];
        const cheapestVolta = [...voltas].sort((a,b) => parseFloat(a.base_price_brl) - parseFloat(b.base_price_brl))[0];

        if (cheapestIda && cheapestVolta) {
            const combinedPrice = parseFloat(cheapestIda.base_price_brl) + parseFloat(cheapestVolta.base_price_brl);
            const priceStr = combinedPrice.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

            comboContainer.innerHTML = `
                <a class="smart-combo-card glass" href="${cheapestIda.booking_url}" target="_blank" rel="noopener noreferrer">
                    <div class="combo-layout">
                        <div class="combo-flights">
                            <div class="combo-flight-row">
                                <span class="combo-badge">Ida</span>
                                <strong>${cheapestIda.airline}</strong> (${cheapestIda.origin} ➔ ${cheapestIda.destination})
                                <span style="color: var(--text-muted); font-size: 0.85rem; margin-left: auto;">${parseFloat(cheapestIda.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</span>
                            </div>
                            <div class="combo-flight-row" style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.5rem; margin-top: 0.25rem;">
                                <span class="combo-badge" style="background: rgba(139, 92, 246, 0.25); color: #c084fc;">Volta</span>
                                <strong>${cheapestVolta.airline}</strong> (${cheapestVolta.origin} ➔ ${cheapestVolta.destination})
                                <span style="color: var(--text-muted); font-size: 0.85rem; margin-left: auto;">${parseFloat(cheapestVolta.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</span>
                            </div>
                        </div>
                        <div class="combo-total-price-section">
                            <span class="combo-total-price-label">Preço Total Combinado</span>
                            <span class="combo-total-price">${priceStr}</span>
                            <span style="font-size: 0.65rem; color: var(--primary); font-weight: 700;">➔ SELECIONAR COMBO (ABRIR IDA)</span>
                        </div>
                    </div>
                </a>
            `;
            comboContainer.classList.remove("hidden");
        }
    }

    // Main search form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!accessToken) {
            alert("Aguarde a autenticação em andamento...");
            return;
        }

        let origin = document.getElementById("origin").value.trim().toUpperCase();
        let dest = document.getElementById("destination").value.trim().toUpperCase();
        const date = document.getElementById("departure_date").value;
        const returnDate = document.getElementById("return_date").value;

        // Parse inputs to obtain 3-letter IATA code
        const originMatch = origin.match(/-\s*([A-Z]{3})\s*$/);
        if (originMatch) origin = originMatch[1];
        const destMatch = dest.match(/-\s*([A-Z]{3})\s*$/);
        if (destMatch) dest = destMatch[1];

        resetSearchState();
        loader.classList.remove("hidden");

        // Helper to load chunks from SSE Stream
        async function fetchStream(fromCode, toCode, dateStr, tripType) {
            try {
                const response = await fetch(`/api/v1/flights/stream?origin=${fromCode}&destination=${toCode}&departure_date=${dateStr}&strategy=cheapest`, {
                    headers: {
                        "Authorization": `Bearer ${accessToken}`
                    }
                });

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
                                    // Append internal properties
                                    const processed = data.flights.map(f => ({
                                        ...f,
                                        tripType: tripType,
                                        collectorName: data.collector
                                    }));
                                    allFlights.push(...processed);
                                    
                                    // Refresh layout, filters, and combinations
                                    sidebar.classList.remove("hidden");
                                    updateAirlineFilters(processed);
                                    applyFiltersAndRender();
                                } else if (data.status === "error") {
                                    console.warn(`Erro no coletor ${data.collector}`, data.error);
                                }
                            } catch (err) {
                                console.error("Parse error no chunk", jsonStr, err);
                            }
                        }
                    }
                }
            } catch (err) {
                console.error(`Stream error for ${tripType}`, err);
            }
        }

        const promises = [fetchStream(origin, dest, date, "IDA")];
        if (returnDate) {
            promises.push(fetchStream(dest, origin, returnDate, "VOLTA"));
        }

        await Promise.all(promises);
        loader.classList.add("hidden");
    });

    // Custom Autocomplete / Typeahead setup
    function setupAutocomplete(inputId, suggestionsId) {
        const input = document.getElementById(inputId);
        const dropdown = document.getElementById(suggestionsId);
        let items = [];
        let activeIndex = -1;
        let debounceTimer;

        async function fetchSuggestions(query) {
            try {
                const response = await fetch(`/api/v1/flights/airports/search?q=${encodeURIComponent(query)}`);
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
                
                div.innerHTML = `
                    <div class="suggestion-info">
                        <span class="suggestion-city-country">${item.city}, ${item.country}</span>
                        <span class="suggestion-airport-name">${item.name}</span>
                    </div>
                    <span class="suggestion-code-badge">${item.code}</span>
                `;

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
                input.value = `${selected.city} (${selected.name}) - ${selected.code}`;
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

    // Dynamic Chart.js logic
    let historyChartInstance = null;

    function loadChartJs() {
        return new Promise((resolve, reject) => {
            if (window.Chart) {
                resolve();
                return;
            }
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/chart.js";
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load Chart.js"));
            document.head.appendChild(script);
        });
    }

    async function openHistoryModal(flightId, airline, routeName) {
        const modal = document.getElementById("history-modal");
        const title = document.getElementById("history-route-title");
        title.textContent = `${airline} | ${routeName}`;
        
        modal.classList.remove("hidden");
        // Force reflow
        modal.offsetWidth;
        modal.classList.add("show");

        try {
            await loadChartJs();
            
            const res = await fetch(`/api/v1/flights/price-history?flight_id=${flightId}`);
            if (!res.ok) throw new Error("API error fetching price history");
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
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#94a3b8' }
                        }
                    }
                }
            });
        } catch (err) {
            console.error("Error rendering chart:", err);
        }
    }

    // Modal Closing Handlers
    document.getElementById("close-history-modal").addEventListener("click", () => {
        const modal = document.getElementById("history-modal");
        modal.classList.remove("show");
        setTimeout(() => modal.classList.add("hidden"), 300);
    });

    const alertModal = document.getElementById("alert-modal");
    document.getElementById("open-alert-btn").addEventListener("click", () => {
        // Validate search fields first
        let origin = document.getElementById("origin").value.trim();
        let dest = document.getElementById("destination").value.trim();
        const date = document.getElementById("departure_date").value;
        
        if (!origin || !dest || !date) {
            alert("Preencha Origem, Destino e Data de Ida para poder criar um alerta de preço.");
            return;
        }

        alertModal.classList.remove("hidden");
        // Force reflow
        alertModal.offsetWidth;
        alertModal.classList.add("show");
    });

    document.getElementById("close-alert-modal").addEventListener("click", () => {
        alertModal.classList.remove("show");
        setTimeout(() => alertModal.classList.add("hidden"), 300);
    });

    // Close modals on clicking outside modal content
    window.addEventListener("click", (e) => {
        const historyModal = document.getElementById("history-modal");
        if (e.target === historyModal) {
            historyModal.classList.remove("show");
            setTimeout(() => historyModal.classList.add("hidden"), 300);
        }
        if (e.target === alertModal) {
            alertModal.classList.remove("show");
            setTimeout(() => alertModal.classList.add("hidden"), 300);
        }
    });

    // Alert form submit handler
    document.getElementById("alert-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        
        let origin = document.getElementById("origin").value.trim().toUpperCase();
        let dest = document.getElementById("destination").value.trim().toUpperCase();
        const date = document.getElementById("departure_date").value;
        
        const originMatch = origin.match(/-\s*([A-Z]{3})\s*$/);
        if (originMatch) origin = originMatch[1];
        const destMatch = dest.match(/-\s*([A-Z]{3})\s*$/);
        if (destMatch) dest = destMatch[1];

        const email = document.getElementById("alert-email").value;
        const telegram = document.getElementById("alert-telegram").value;
        const targetPrice = parseFloat(document.getElementById("alert-price").value);

        try {
            const res = await fetch("/api/v1/flights/alerts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    telegram_chat_id: telegram || null,
                    origin: origin,
                    destination: dest,
                    departure_date: date,
                    target_price: targetPrice
                })
            });

            if (!res.ok) throw new Error("Failed to create price alert");
            const data = await res.json();
            
            alert(data.message || "Alerta de preço ativado com sucesso!");
            
            // Clear and close
            document.getElementById("alert-form").reset();
            alertModal.classList.remove("show");
            setTimeout(() => alertModal.classList.add("hidden"), 300);
        } catch (err) {
            console.error("Error creating price alert:", err);
            alert("Erro ao cadastrar alerta. Tente novamente.");
        }
    });
});
