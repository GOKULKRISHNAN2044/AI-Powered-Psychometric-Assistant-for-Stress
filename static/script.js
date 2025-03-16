let questions = [];
let currentQuestion = 0;
let scores = { Stable: 0, Anxious: 0, Depressive: 0, Impulsive: 0 };

// Load questions dynamically from Flask
fetch("/get_questions")
    .then(response => response.json())
    .then(data => {
        questions = data;
        loadQuestion();
    });

function loadQuestion() {
    if (currentQuestion < questions.length) {
        document.getElementById("question").innerText = questions[currentQuestion][0];
        let optionsDiv = document.getElementById("options");
        optionsDiv.innerHTML = "";
        for (let i = 1; i <= 4; i++) {
            let btn = document.createElement("button");
            btn.innerText = questions[currentQuestion][i];
            btn.onclick = function() { recordResponse(i - 1); };
            optionsDiv.appendChild(btn);
        }
    } else {
        submitResults();
    }
}

function recordResponse(index) {
    let traits = ["Stable", "Anxious", "Depressive", "Impulsive"];
    scores[traits[index]]++;
    currentQuestion++;
    loadQuestion();
}

function submitResults() {
    fetch("/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scores })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("stress-level").innerText = `Predicted Stress Level: ${data.stress_level}`;
        document.getElementById("report").innerText = data.report;
        updateGauge(data.stress_level);
    });
}

function updateGauge(level) {
    let ctx = document.getElementById("stressGauge").getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Low", "Medium", "High"],
            datasets: [{
                data: [level === "Low" ? 1 : 0, level === "Moderate" ? 1 : 0, level === "High" ? 1 : 0],
                backgroundColor: ["green", "yellow", "red"]
            }]
        },
        options: { responsive: true }
    });
}
