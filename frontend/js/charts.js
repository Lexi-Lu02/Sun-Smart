const API = "https://m4d1jzxb7.execute-api.ap-southeast-2.amazonaws.com/default/sunsmart-data-api"

document.addEventListener("DOMContentLoaded", () => {
  loadAgeChart()
  loadStateChart()
  loadMortalityChart()
  loadTips()
})

async function loadAgeChart() {
  const res = await fetch(`${API}?type=age`)
  const data = await res.json()

  new Chart(document.getElementById("ageChart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: data.datasetLabel,
        data: data.values
      }]
    }
  })
}

async function loadStateChart() {
  const res = await fetch(`${API}?type=state`)
  const data = await res.json()

  new Chart(document.getElementById("stateChart"), {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: data.datasetLabel,
        data: data.values
      }]
    }
  })
}

async function loadMortalityChart() {
  const res = await fetch(`${API}?type=mortality`)
  const data = await res.json()

  new Chart(document.getElementById("mortalityChart"), {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [{
        label: data.datasetLabel,
        data: data.values
      }]
    }
  })
}

async function loadTips() {
  const res = await fetch(`${API}?type=sun`)
  const data = await res.json()

  const container = document.getElementById("tipList")
  container.innerHTML = ""

  data.tips.forEach(tip => {
    const div = document.createElement("div")
    div.className = "fact-item"
    div.innerHTML = `
      <div class="fact-badge">Tip</div>
      <p>${tip}</p>
    `
    container.appendChild(div)
  })

  document.getElementById("keyTakeaway").innerText = data.takeaway
}