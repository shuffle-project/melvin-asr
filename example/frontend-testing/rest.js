let selectedFile = null;
const responseTextContainer = document.getElementById('transcriptionResponse');
const transcriptionFileName = document.getElementById('transcriptionFileName');


/**
 * On window load, retrieve and set the API key from localStorage.
 * If an API key is found, it is populated in the input field.
 */
window.onload = function() {
    // Retrieve the stored API key from localStorage
    const storedApiKey = localStorage.getItem('apiKey');
    
    // If an API key exists, set it in the input field
    if (storedApiKey) {
        document.getElementById('apiKey').value = storedApiKey;
    }
};

/**
 * Function to check the health status of the API on window load.
 * Updates the 'checkHealth' element with the status of the service.
 */
window.onload = async function checkHealth() {
    const responseContainer = document.getElementById('checkHealth');
    responseContainer.textContent = 'Calling API...';

    const apiKey = localStorage.getItem('apiKey');  // Retrieve the saved API key
    if (!apiKey) {
        responseContainer.textContent = 'API key is missing. Please save your API key first.';
        return;
    }

    try {
        // Make a GET request to the health check endpoint
        const response = await fetch('http://localhost:8393/health', {
            method: 'GET',
            headers: {
                'Authorization': `${apiKey}`
            }
        });

        // Check if the response is successful
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        } else {
            // Update the response container with the service status
            responseContainer.textContent = 'Authorized - Service is running';
        }
    } catch (error) {
        // Display error message in case of request failure
        responseContainer.textContent = 'Could not reach API / API Key missing';
    }
}

/**
 * Save the API key to localStorage
 * @param {string} apiKey - The API key to save
 */
function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    if (apiKey) {
        localStorage.setItem('apiKey', apiKey);
        const responseContainer = document.getElementById('checkHealth');
        responseContainer.textContent = "API Key saved successfully!";
    } else {
        const responseContainer = document.getElementById('checkHealth');
        responseContainer.textContent = "Please enter a valid API key first.";
    }
}

function allowDrop(event) {
    event.preventDefault();  // Allow file to be dropped
}

function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        selectedFile = files[0];
        document.getElementById('dropZone').textContent = `Selected file: ${selectedFile.name}`;
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        selectedFile = files[0];
        document.getElementById('dropZone').textContent = `Selected file: ${selectedFile.name}`;
    }
}

document.getElementById('dropZone').addEventListener('click', () => {
    document.getElementById('fileInput').click();  // Open file selector dialog
});

/**
 * Function to start transcription by sending a selected file to the API.
 * Displays the response or error in the 'response' element.
 */
async function requestTranscription() {
    const responseContainer = document.getElementById('response');

    // Check if a file is selected
    if (!selectedFile) {
        responseContainer.textContent = 'Please upload a file first.';
        return;
    }

    const formData = new FormData();

    const apiKey = localStorage.getItem('apiKey');  // Retrieve the saved API key
    if (!apiKey) {
        responseContainer.textContent = 'API key is missing. Please save your API key first.';
        return;
    }

    // Verify selected file is valid
    if (selectedFile === null || selectedFile === undefined) {
        responseContainer.textContent = 'No file selected.';
        return;
    }
    
    // Append necessary data to FormData object
    formData.append('file', selectedFile);
    formData.append('test', 'test');
    formData.append('language', 'en');
    formData.append('settings', '{"test": "test"}');
    formData.append('model', 'large-v3');

    responseContainer.textContent = 'Calling API...';

    try {
        // Make POST request to transcription API
        const response = await fetch('http://localhost:8393/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `${apiKey}`
            },
            body: formData
        });

        // Check response status
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        // Parse and display response data
        const data = await response.json();
        responseContainer.textContent = JSON.stringify(data, null, 2);
        transcriptionFileName.textContent = "File name: " + selectedFile.name;
        responseTextContainer.textContent = data['transcription_id'];
    } catch (error) {
        // Display error message on failure
        responseContainer.textContent = error.message;
    }
}

async function requestTranscriptionText() {
    transcription_id = "287c4ded-ecdc-4938-9b56-78e3ab8b1f3d";

    const apiKey = localStorage.getItem('apiKey');  // Retrieve the saved API key
    if (!apiKey) {
        responseContainer.textContent = 'API key is missing. Please save your API key first.';
        return;
    }

    responseTextContainer.textContent = 'Calling API...';

    try {
        // Make POST request to transcription API
        const response = await fetch(`http://localhost:8393/transcript/${transcription_id}`, {
            method: 'GET',
            headers: {
                'Authorization': `${apiKey}`
            },
        });

        // Check response status
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        // Parse and display response data
        const data = await response.json();

        responseTextContainer.textContent = data.stringify(data, null, 2); //data['transcript']['text'];
    } catch (error) {
        // Display error message on failure
        responseTextContainer.textContent = error.message;
    }
}