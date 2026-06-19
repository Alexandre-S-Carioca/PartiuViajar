document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("search-form");
    const grid = document.getElementById("flights-grid");
    const loader = document.getElementById("loader");

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

        const origin = document.getElementById("origin").value.toUpperCase();
        const dest = document.getElementById("destination").value.toUpperCase();
        const date = document.getElementById("departure_date").value;
        const returnDate = document.getElementById("return_date").value;

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
            const card = document.createElement("div");
            card.className = "flight-card glass";
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
});
