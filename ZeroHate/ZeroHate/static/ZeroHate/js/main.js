document.getElementById('classification-form').addEventListener('submit', function (event) {
    event.preventDefault();  // Prevent default form submission

    const text = document.getElementById('input-text').value;

    document.getElementById('input-text').value = ""
    classifyText(text)
});



function classifyText(text) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Show the loader
    const btnLoader = document.querySelector('.btn-loader');
    btnLoader.classList.remove('hidden');
    // Make AJAX request
    fetch('/classify-text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (response.status === 429) {
          // Handle rate limit exceeded
          alert('Rate limit exceeded. Please try again later.');
          return Promise.reject('rate_limited');
        } else if (!response.ok) {
          throw new Error('An error occurred');
        }
        return response.json();
      })
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
            if (error === 'rate_limited') return;  // don’t alert twice for rate limit
            // Hide the loader and show an error message
            btnLoader.classList.add('hidden');
            alert('An error occurred: ' + error);
        });
}
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






document.getElementById('upload-file-btn').addEventListener('click', function () {
    document.getElementById('file-upload').click();  // Trigger the hidden file input
});

document.getElementById('file-upload').addEventListener('change', function () {
    var fileInput = document.getElementById('file-upload');
    var file = fileInput.files[0];  // Get the selected file

    if (file) {
        var formData = new FormData();
        formData.append('file', file);  // Append the file to form data

        // Get the CSRF token from the template and add it to the request headers
        var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

        // Make an AJAX request to upload the file
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload_file/', true);  // Django view URL
        xhr.setRequestHeader('X-CSRFToken', csrfToken);  // Include CSRF token in the header

        // Handle the response
        xhr.onload = function () {
            if (xhr.status === 200) {
                console.log('File uploaded successfully');
                const response = JSON.parse(xhr.responseText);
                console.log(response);  // { message: "...", file_url: "...", text: "..." }
                classifyText(response.text);  // Pass the extracted text
            } else {
                console.log('Error uploading file');
            }
        };

        xhr.send(formData);  // Send the file data to the server
    } else {
        console.log('No file selected');
    }
});
