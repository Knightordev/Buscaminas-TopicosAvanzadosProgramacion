document.addEventListener("DOMContentLoaded", function () {
    const table = document.getElementById("table");

    if (!table) {
        return;
    }

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
        cell.textContent = "🚩";
        cell.dataset.flagged = "1";
        cell.style.background = "#f1c40f";
        cell.style.color = "#2c3e50";
    }

    function showRevealedCell(cell, data) {
        if (data.type === "mine") {
    alert("💣 Perdiste — Puntaje: " + data.puntaje);
}
        cell.dataset.revealed = "1";
        cell.dataset.flagged = "0";

        if (data.type === "mine") {
            cell.textContent = "💣";
            cell.style.background = "#e74c3c";
            cell.style.color = "white";
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

    table.addEventListener("click", async function (e) {
        if (e.target.tagName !== "TD") {
            return;
        }

        const cell = e.target;

        if (cell.dataset.revealed === "1" || cell.dataset.flagged === "1") {
            return;
        }

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

            if (data.type === "mine") {
                showRevealedCell(cell, { type: "mine" });
                alert("💣 Perdiste - Puntaje: " + data.puntaje);
                return;
            }

            if (data.type === "reveal") {
                data.cells.forEach(function (revealedCell) {
                    const targetRow = table.rows[revealedCell.row];
                    const targetCell = targetRow.cells[revealedCell.col];

                    showRevealedCell(targetCell, {
                        type: "number",
                        value: revealedCell.number
                    });
                });
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

