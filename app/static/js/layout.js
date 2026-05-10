document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("table");

    if (!table) {
        return;
    }

    // ─── TEMPORIZADOR ────────────────────────────────────────────────────────────
    let timerStarted = false;
    let timerInterval = null;
    let elapsedSeconds = 0;
    const PENALTY_START = 180; // 3 minutos en segundos

    const timerEl = document.getElementById("timer-display");

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60).toString().padStart(2, "0");
        const s = (seconds % 60).toString().padStart(2, "0");
        return `${m}:${s}`;
    }

    function startTimer() {
        if (timerStarted) return;
        timerStarted = true;
        timerInterval = setInterval(() => {
            elapsedSeconds++;
            if (timerEl) {
                timerEl.textContent = "⏱ " + formatTime(elapsedSeconds);
                if (elapsedSeconds >= PENALTY_START) {
                    timerEl.style.color = "#e74c3c";
                    timerEl.style.fontWeight = "bold";
                } else if (elapsedSeconds >= PENALTY_START - 30) {
                    timerEl.style.color = "#f39c12";
                }
            }
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
    }

    function calcularPuntajeConTiempo(puntajeBase) {
        if (elapsedSeconds <= PENALTY_START) {
            return puntajeBase;
        }
        const penalizacion = elapsedSeconds - PENALTY_START;
        return Math.max(0, puntajeBase - penalizacion);
    }
    // ─────────────────────────────────────────────────────────────────────────────

    const colors = [
        "",
        "#3498db",
        "#27ae60",
        "#e74c3c",
        "#8e44ad",
        "#c0392b",
        "#16a085",
        "#2c3e50",
        "#7f8c8d"
    ];

    function getCellPosition(cell) {
        return {
            row: cell.parentNode.rowIndex,
            col: cell.cellIndex
        };
    }

    function clearCell(cell) {
        cell.textContent = "";
        cell.dataset.revealed = "0";
        cell.dataset.flagged = "0";
        cell.style.background = "";
        cell.style.color = "";
    }

    function showFlag(cell) {
        cell.textContent = "🛡️";
        cell.dataset.flagged = "1";
        cell.style.background = "#f1c40f";
        cell.style.color = "#2c3e50";
    }

    function updateVidas(vidas) {
        const vidasEl = document.getElementById("vidas-counter");
        if (vidasEl) {
            vidasEl.textContent = "Vidas: " + "❤️".repeat(vidas);
        }
    }

    function showRevealedCell(cell, data) {
        cell.dataset.revealed = "1";
        cell.dataset.flagged = "0";

        if (data.type === "mine") {
            cell.textContent = "💀";
            cell.style.background = "#e74c3c";
            cell.style.color = "white";
            return;
        }

        if (data.extra_life) {
            cell.textContent = "💚";
            cell.style.background = "#ecf0f1";
            return;
        }

        if (data.value === 0) {
            cell.textContent = "";
        } else {
            cell.textContent = data.value;
        }

        cell.style.background = "#ecf0f1";

        if (data.value > 0) {
            cell.style.color = colors[data.value] || "#000";
        } else {
            cell.style.color = "";
        }
    }

    async function guardarPuntaje(puntaje) {
        let nombre = prompt("¿Cuál es tu nombre?", "");
        if (!nombre || nombre.trim() === "") nombre = "Jugador";

        await fetch('/guardar_puntaje', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: nombre.trim(), puntaje: puntaje })
        });

        return nombre.trim();
    }

    table.addEventListener("click", async function (e) {
        if (e.target.tagName !== "TD") {
            return;
        }

        const cell = e.target;

        if (cell.dataset.revealed === "1" || cell.dataset.flagged === "1") {
            return;
        }

        startTimer();

        const position = getCellPosition(cell);
        cell.style.opacity = "0.5";

        try {
            const response = await fetch(`/reveal/${position.row}/${position.col}`, {
                method: "POST"
            });

            const data = await response.json();
            cell.style.opacity = "1";

            if (!response.ok) {
                return;
            }

            if (data.already_revealed || data.blocked === "flagged") {
                return;
            }

            if (data.type === "hit") {
                showRevealedCell(cell, { type: "mine" });
                updateVidas(data.vidas);
                alert("💥 ¡Pisaste una mina! Te queda " + data.vidas + " vida(s)");
                return;
            }

            if (data.type === "mine") {
                stopTimer();
                showRevealedCell(cell, { type: "mine" });
                const puntajeFinal = calcularPuntajeConTiempo(data.puntaje);
                const nombre = await guardarPuntaje(puntajeFinal);
                const tiempoMsg = elapsedSeconds > PENALTY_START
                    ? `\n⏱ Tiempo: ${formatTime(elapsedSeconds)} (penalización aplicada)`
                    : `\n⏱ Tiempo: ${formatTime(elapsedSeconds)}`;
                alert(`💣 ¡Perdiste, ${nombre}!\nPuntaje base: ${data.puntaje}\nPuntaje final: ${puntajeFinal}${tiempoMsg}`);
                window.location.href = "/";
                return;
            }

            if (data.type === "reveal") {
                data.cells.forEach(function (revealedCell) {
                    const targetRow = table.rows[revealedCell.row];
                    const targetCell = targetRow.cells[revealedCell.col];

                    showRevealedCell(targetCell, {
                        type: "number",
                        value: revealedCell.number,
                        extra_life: revealedCell.extra_life
                    });
                });

                if (data.got_extra_life) {
                    updateVidas(data.vidas);
                    alert("💚 ¡Encontraste una vida extra!");
                }

                if (data.win) {
                    stopTimer();
                    const puntajeFinal = calcularPuntajeConTiempo(data.puntaje);
                    const nombre = await guardarPuntaje(puntajeFinal);
                    const tiempoMsg = elapsedSeconds > PENALTY_START
                        ? `\n⏱ Tiempo: ${formatTime(elapsedSeconds)} (penalización aplicada)`
                        : `\n⏱ Tiempo: ${formatTime(elapsedSeconds)}`;
                    alert(`🎉 ¡Ganaste, ${nombre}!\nPuntaje base: ${data.puntaje}\nPuntaje final: ${puntajeFinal}${tiempoMsg}`);
                    window.location.href = "/";
                }
            }
        } catch (error) {
            cell.style.opacity = "1";
            console.error("Error:", error);
        }
    });

    table.addEventListener("contextmenu", async function (e) {
        if (e.target.tagName !== "TD") {
            return;
        }

        e.preventDefault();

        const cell = e.target;

        if (cell.dataset.revealed === "1") {
            return;
        }

        const position = getCellPosition(cell);

        try {
            const response = await fetch("/toggle_flag", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    r: position.row,
                    c: position.col
                })
            });

            const data = await response.json();
            const flagCounter = document.getElementById("flag-counter");

            if (!response.ok || data.status !== "success") {
                return;
            }

            if (data.is_flagged) {
                showFlag(cell);
            } else {
                clearCell(cell);
            }

            if (flagCounter) {
                flagCounter.textContent = `Flags: ${data.total_flags} / ${data.total_mines}`;
            }
        } catch (error) {
            console.error("Error:", error);
        }
    });
});
