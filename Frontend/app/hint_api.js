(() => {
  const backendBase =
    window.BACKEND_URL ||
    `${window.location.protocol}//${window.location.hostname}:8080`;

  function buildGrid() {
    const grid = Array.from({ length: 9 }, () => Array(9).fill(0));
    document.querySelectorAll(".cell").forEach((cell) => {
      const row = parseInt(cell.dataset.r, 10);
      const col = parseInt(cell.dataset.c, 10);
      if (Number.isNaN(row) || Number.isNaN(col)) {
        return;
      }
      if (cell.classList.contains("fixed")) {
        const value = parseInt(cell.textContent, 10);
        if (!Number.isNaN(value)) {
          grid[row][col] = value;
        }
      }
    });
    return grid;
  }

  async function getHintFromBackend() {
    const targetCell = document.querySelector(".cell.target");
    if (!targetCell) {
      return;
    }

    const targetRow = parseInt(targetCell.dataset.r, 10);
    const targetCol = parseInt(targetCell.dataset.c, 10);
    if (Number.isNaN(targetRow) || Number.isNaN(targetCol)) {
      return;
    }

    const payload = {
      grid: buildGrid(),
      target: { row: targetRow, col: targetCol },
    };

    let res;
    try {
      res = await fetch(`${backendBase}/ia/hint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      console.error(err);
      return;
    }

    if (!res.ok) {
      return;
    }

    const data = await res.json();
    if (!data || data.error) {
      return;
    }

    const cellEl = document.querySelector(
      `.cell[data-r="${data.row}"][data-c="${data.col}"]`
    );
    if (!cellEl) {
      return;
    }

    cellEl.textContent = data.value;
    cellEl.classList.add("fixed");
    cellEl.onclick = null;
  }

  window.getHint = getHintFromBackend;
})();
