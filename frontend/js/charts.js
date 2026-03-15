const API = "http://16.176.142.118:8000/api/awareness"

document.addEventListener("DOMContentLoaded", () => {

  loadAgeChart()
  loadStateChart()
  loadMortalityChart()
  loadTips()

})

async function loadAgeChart(){

  const res = await fetch(`${API}/incidence-age`)
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

async function loadStateChart(){

  const res = await fetch(`${API}/incidence-state`)
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

async function loadMortalityChart(){

  const res = await fetch(`${API}/mortality`)
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

async function loadTips(){

  const res = await fetch(`${API}/sunprotection`)
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