const API = " https://md4j1zjxb7.execute-api.ap-southeast-2.amazonaws.com/default/sunsmart-data-api";

document.addEventListener("DOMContentLoaded", () => {
  loadAgeChart();
  loadStateChart();
  loadMortalityChart();
  loadTips();
});

async function fetchJson(type) {
  const res = await fetch(`${API}?type=${type}`);

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }

  return await res.json();
}

function hideElement(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "none";
}

function showElement(id, display = "block") {
  const el = document.getElementById(id);
  if (el) el.style.display = display;
}

function showError(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("hidden");
}

function sanitizeChartData(data) {
  if (!data || !Array.isArray(data.labels) || !Array.isArray(data.values)) {
    throw new Error("Invalid chart data format");
  }

  const cleanedLabels = [];
  const cleanedValues = [];

  for (let i = 0; i < data.labels.length; i++) {
    const label = data.labels[i];
    const value = data.values[i];

    if (label === undefined || label === null || label === "") continue;

    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) continue;

    cleanedLabels.push(label);
    cleanedValues.push(numericValue);
  }

  return {
    labels: cleanedLabels,
    values: cleanedValues,
    datasetLabel: data.datasetLabel || "Dataset"
  };
}

function createBarChart(canvasId, data) {
  new Chart(document.getElementById(canvasId), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: data.datasetLabel,
          data: data.values,
          backgroundColor: "rgba(54, 162, 235, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#cbd5e1"
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#94a3b8",
            maxRotation: 45,
            minRotation: 45
          },
          grid: {
            color: "rgba(255,255,255,0.05)"
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: "#94a3b8"
          },
          grid: {
            color: "rgba(255,255,255,0.05)"
          }
        }
      }
    }
  });
}

function createLineChart(canvasId, data) {
  new Chart(document.getElementById(canvasId), {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: data.datasetLabel,
          data: data.values,
          borderColor: "rgba(255, 159, 64, 1)",
          backgroundColor: "rgba(255, 159, 64, 0.2)",
          borderWidth: 2,
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#cbd5e1"
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: "#94a3b8",
            maxRotation: 45,
            minRotation: 45
          },
          grid: {
            color: "rgba(255,255,255,0.05)"
          }
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: "#94a3b8"
          },
          grid: {
            color: "rgba(255,255,255,0.05)"
          }
        }
      }
    }
  });
}

async function loadAgeChart() {
  try {
    const rawData = await fetchJson("age");
    const data = sanitizeChartData(rawData);

    hideElement("ageLoading");
    createBarChart("ageChart", data);
  } catch (err) {
    console.error("Age chart error:", err);
    hideElement("ageLoading");
    showError("ageError");
  }
}

async function loadStateChart() {
  try {
    const rawData = await fetchJson("state");
    const data = sanitizeChartData(rawData);

    hideElement("stateLoading");
    createBarChart("stateChart", data);
  } catch (err) {
    console.error("State chart error:", err);
    hideElement("stateLoading");
    showError("stateError");
  }
}

async function loadMortalityChart() {
  try {
    const rawData = await fetchJson("mortality");
    const data = sanitizeChartData(rawData);

    hideElement("mortalityLoading");
    createLineChart("mortalityChart", data);
  } catch (err) {
    console.error("Mortality chart error:", err);
    hideElement("mortalityLoading");
    showError("mortalityError");
  }
}

async function loadTips() {
  try {
    const data = await fetchJson("sun");

    const container = document.getElementById("tipList");
    if (container) {
      container.innerHTML = "";

      if (Array.isArray(data.tips)) {
        data.tips.forEach(tip => {
          const div = document.createElement("div");
          div.className = "fact-item";
          div.innerHTML = `
            <div class="fact-badge">TIP</div>
            <p>${tip}</p>
          `;
          container.appendChild(div);
        });
      }
    }

    const takeaway = document.getElementById("keyTakeaway");
    if (takeaway) {
      takeaway.innerText = data.takeaway || "Stay sun safe.";
    }
  } catch (err) {
    console.error("Tips error:", err);

    const container = document.getElementById("tipList");
    if (container) {
      container.innerHTML = `<div class="error-text">Failed to load tips.</div>`;
    }

    const takeaway = document.getElementById("keyTakeaway");
    if (takeaway) {
      takeaway.innerText = "Unable to load takeaway.";
    }
  }
}