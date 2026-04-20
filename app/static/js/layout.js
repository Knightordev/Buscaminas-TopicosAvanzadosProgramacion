document.addEventListener("DOMContentLoaded", function() {

    const tabla = document.getElementById("table");

    tabla.addEventListener("click", async function(e) {
        if (e.target.tagName !== "TD") return;

        const celda = e.target;
        if (celda.dataset.revealed === "1") return;

        const col = celda.cellIndex;
        const row = celda.parentNode.rowIndex;

        celda.style.opacity = "0.5";

        try {
            const res = await fetch(`/reveal/${row}/${col}`, { method: "POST" });
            const data = await res.json();

            celda.style.opacity = "1";
            celda.dataset.revealed = "1";

            if (data.type === "mine") {
                celda.textContent = "💣";
                celda.style.background = "#e74c3c";
                celda.style.color = "white";
            } else if (data.type === "number") {
                celda.textContent = data.value === 0 ? "" : data.value;
                celda.style.background = "#ecf0f1";
                const colors = ["", "#3498db", "#27ae60", "#e74c3c", "#8e44ad",
                                "#c0392b", "#16a085", "#2c3e50", "#7f8c8d"];
                if (data.value > 0) celda.style.color = colors[data.value] || "#000";
            }
        } catch (err) {
            celda.style.opacity = "1";
            console.error("Error:", err);
        }
    });

});