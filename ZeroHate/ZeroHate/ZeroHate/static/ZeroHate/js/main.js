document.getElementById('classification-form').addEventListener('submit', function (event) {
    console.log("Called")
    event.preventDefault();  // Prevent default form submission

    const text = document.getElementById('input-text').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Show the loader
    const btnLoader = document.querySelector('.btn-loader');
    btnLoader.classList.remove('hidden');

    document.getElementById('input-text').value = ""
    // Make AJAX request
    fetch('/classify-text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ text: text })
    })
        .then(response => response.json())
        .then(data => {
            // Hide the loader
            btnLoader.classList.add('hidden');

            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                // Create a new result card and append it to results container
                const resultsContainer = document.getElementById('results-container');
                const resultCard = createResultCard(data);
                resultsContainer.innerHTML = ""
                resultsContainer.appendChild(resultCard);
            }
        })
        .catch(error => {
            // Hide the loader and show an error message
            btnLoader.classList.add('hidden');
            alert('An error occurred: ' + error);
        });
});

// Function to create a new result card
function createResultCard(data) {
    const card = document.createElement('div');
    card.classList.add('classifier-card');

    card.innerHTML = `
            <div class="card-header">
                <h3>Classification Results</h3>
            </div>
            <div class="card-body">
                <p class="score-row-text"><strong>Text:</strong> ${data.text}</p>
                <p class="score-row"><strong>Toxicity Chance:</strong> <span>${(data.toxic * 100).toFixed(1)}%</span></p>
                <p class="score-row"><strong>Severe Toxicity Chance:</strong> <span>${(data.severe_toxic * 100).toFixed(1)}%</span></p>
                <p class="score-row"><strong>Obscene Chance:</strong> <span>${(data.obscene * 100).toFixed(1)}%</span></p>
                <p class="score-row"><strong>Threat Chance:</strong> <span>${(data.threat * 100).toFixed(1)}%</span></p>
                <p class="score-row"><strong>Insult Chance:</strong> <span>${(data.insult * 100).toFixed(1)}%</span></p>
                <p class="score-row"><strong>Identity Hate Chance:</strong> <span>${(data.identity_hate * 100).toFixed(1)}%</span></p>
            </div>
        `;

    return card;
}
