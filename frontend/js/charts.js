document.addEventListener("DOMContentLoaded", async () => {

  const API_BASE = "http://127.0.0.1:8000/api/awareness";

  const skinCtx = document.getElementById("skinCancerChart");
  const heatCtx = document.getElementById("heatTrendChart");

  // Skin cancer chart
  if (skinCtx) {

    const res = await fetch(`${API_BASE}/skin-cancer`);
    const data = await res.json();

    new Chart(skinCtx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [{
          label: data.datasetLabel || "Skin Cancer Impact",
          data: data.values,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: "#eef2ff" }
          }
        },
        scales: {
          x: {
            ticks: { color: "#9fb0cf" },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y: {
            beginAtZero: true,
            ticks: { color: "#9fb0cf" },
            grid: { color: "rgba(255,255,255,0.08)" }
          }
        }
      }
    });
  }

  // Heat trend chart
  if (heatCtx) {

    const res = await fetch(`${API_BASE}/heat-trend`);
    const data = await res.json();

    new Chart(heatCtx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [{
          label: data.datasetLabel || "Heat Trend in Australia",
          data: data.values,
          tension: 0.35,
          fill: false
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            labels: { color: "#eef2ff" }
          }
        },
        scales: {
          x: {
            ticks: { color: "#9fb0cf" },
            grid: { color: "rgba(255,255,255,0.08)" }
          },
          y: {
            ticks: { color: "#9fb0cf" },
            grid: { color: "rgba(255,255,255,0.08)" }
          }
        }
      }
    });
  }

});