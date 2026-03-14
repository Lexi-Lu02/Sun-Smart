document.addEventListener("DOMContentLoaded", () => {
  const skinCtx = document.getElementById("skinCancerChart");
  const heatCtx = document.getElementById("heatTrendChart");

  if (skinCtx) {
    new Chart(skinCtx, {
      type: "bar",
      data: {
        labels: ["15–24", "25–34", "35–44", "45–54", "55+"],
        datasets: [{
          label: "Skin Cancer Impact (example data)",
          data: [12, 18, 27, 35, 49],
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

  if (heatCtx) {
    new Chart(heatCtx, {
      type: "line",
      data: {
        labels: ["2019", "2020", "2021", "2022", "2023", "2024"],
        datasets: [{
          label: "Heat Trend in Australia (example data)",
          data: [26.1, 26.4, 26.8, 27.2, 27.6, 28.1],
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