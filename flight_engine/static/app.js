document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("search-form");
    const grid = document.getElementById("flights-grid");
    const loader = document.getElementById("loader");

    // Limpar campos do formulário ao carregar (F5)
    if (form) {
        form.reset();
        document.getElementById("origin").value = "";
        document.getElementById("destination").value = "";
        document.getElementById("departure_date").value = "";
        document.getElementById("return_date").value = "";
    }

    let accessToken = "";

    // Autenticação mock background
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

        // Extract 3-letter code if input contains " - XXX" (e.g. from dropdown selection)
        const originMatch = origin.match(/-\s*([A-Z]{3})\s*$/);
        if (originMatch) {
            origin = originMatch[1];
        }
        const destMatch = dest.match(/-\s*([A-Z]{3})\s*$/);
        if (destMatch) {
            dest = destMatch[1];
        }

        // Limpar tela
        grid.innerHTML = "";
        loader.classList.remove("hidden");

        // Função isolada para abrir uma conexão de Stream (Ida ou Volta)
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
                                if (data.status === "success") {
                                    renderFlights(data.flights, data.collector, tripType);
                                } else {
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

    function renderFlights(flights, collectorName, tripType) {
        flights.forEach((flight, index) => {
            const card = document.createElement("a");
            card.className = "flight-card glass";
            card.href = flight.booking_url || "#";
            card.target = "_blank";
            card.rel = "noopener noreferrer";
            card.style.animationDelay = `${index * 0.1}s`;

            // Formatando Data
            const dateObj = new Date(flight.departure_date);
            const dateStr = dateObj.toLocaleDateString("pt-BR", { day: '2-digit', month: '2-digit', hour: '2-digit', minute:'2-digit' });

            // Formatando Preço
            const price = parseFloat(flight.base_price_brl).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

            card.innerHTML = `
                <div class="card-header">
                    <span class="airline">
                        <span style="font-size: 0.7em; background: rgba(59, 130, 246, 0.2); padding: 2px 6px; border-radius: 4px; color: var(--primary); margin-right: 8px;">${tripType}</span>
                        ${flight.airline || "Voo"} 
                        <small style="font-size:0.6em;color:var(--text-muted)">(${collectorName})</small>
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
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Custom Autocomplete / Typeahead setup
    function setupAutocomplete(inputId, suggestionsId) {
        const input = document.getElementById(inputId);
        const dropdown = document.getElementById(suggestionsId);
        let items = [];
        let activeIndex = -1;
        let debounceTimer;

        // Fetch suggestions from API
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

        // Render dropdown list
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
                    // Prevent input blur before click event registers selection
                    e.preventDefault();
                    selectItem(index);
                });
                dropdown.appendChild(div);
            });

            dropdown.classList.remove("hidden");
        }

        // Highlight selected suggestion (keyboard nav)
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

        // Handle item selection
        function selectItem(index) {
            if (index >= 0 && index < items.length) {
                const selected = items[index];
                input.value = `${selected.city} (${selected.name}) - ${selected.code}`;
                dropdown.classList.add("hidden");
                dropdown.innerHTML = "";
                activeIndex = -1;
            }
        }

        // Event listener for typing
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
            }, 150); // 150ms debounce
        });

        // Event listener for keyboard navigation
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

        // Close dropdown when clicking outside
        document.addEventListener("click", (e) => {
            if (e.target !== input && !dropdown.contains(e.target)) {
                dropdown.classList.add("hidden");
                activeIndex = -1;
            }
        });

        // Show suggestions on focus if there is text
        input.addEventListener("focus", async () => {
            const query = input.value.trim();
            // Don't show if it's already a full formatted string
            if (query && !query.includes(" - ")) {
                const suggestions = await fetchSuggestions(query);
                renderDropdown(suggestions);
            }
        });
    }

    // Initialize Autocomplete for Origin and Destination fields
    setupAutocomplete("origin", "origin-suggestions");
    setupAutocomplete("destination", "destination-suggestions");
});
