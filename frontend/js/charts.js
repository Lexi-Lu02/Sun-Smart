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

async function loadAgeChart() {
  const data = await fetchJson("age");

  new Chart(document.getElementById("ageChart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: data.datasetLabel,
          data: data.values
        }
      ]
    }
  });
}

async function loadStateChart() {
  const data = await fetchJson("state");

  new Chart(document.getElementById("stateChart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: data.datasetLabel,
          data: data.values
        }
      ]
    }
  });
}

async function loadMortalityChart() {
  const data = await fetchJson("mortality");

  new Chart(document.getElementById("mortalityChart"), {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: data.datasetLabel,
          data: data.values
        }
      ]
    }
  });
}

async function loadTips() {
  const data = await fetchJson("sun");

  const container = document.getElementById("tipList");
  container.innerHTML = "";

  if (Array.isArray(data.tips)) {
    data.tips.forEach(tip => {
      const div = document.createElement("div");
      div.className = "fact-item";
      div.innerHTML = `
        <div class="fact-badge">Tip</div>
        <p>${tip}</p>
      `;
      container.appendChild(div);
    });
  }

  if (data.takeaway) {
    document.getElementById("keyTakeaway").innerText = data.takeaway;
  }
}