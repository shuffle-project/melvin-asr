const API_URL = 'http://localhost:8393/transcriptions/';
const DEFAULT_LANGUAGE = 'en';
const DEFAULT_MODEL = 'large-v3-turbo';
const SETTINGS = '{"test": "test"}';
const ERROR_MESSAGES = {
    NO_FILE: 'Please upload a file first.',
    MISSING_API_KEY: 'API key is missing. Please save your API key first.',
    INVALID_API_KEY: 'Invalid API key. Please save your API key first.',
};

let selectedFile = null;
const apiResponse = document.getElementById('apiResponse');
const responseTextContainer = document.getElementById('transcriptionResponse');
const transcriptionFileName = document.getElementById('transcriptionFileName');
const loadingContainer = document.getElementById('loadingContainer');

const loadingSVG =
    `<svg class="spinner" width="65px" height="65px" viewBox="0 0 66 66" xmlns="http://www.w3.org/2000/svg">
   <circle class="path" fill="none" stroke-width="6" stroke-linecap="round" cx="33" cy="33" r="30"></circle>
</svg>`;

// Helper function to retrieve API key
const getApiKey = () => localStorage.getItem('apiKey');

// Helper function to create FormData
const createFormData = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('test', 'test');
    formData.append('language', DEFAULT_LANGUAGE);
    formData.append('settings', SETTINGS);
    formData.append('model', DEFAULT_MODEL);
    return formData;
};

// Helper function to handle API error response display
const displayError = (container, message) => {
    container.textContent = message;
};

/**
 * On window load, retrieve and set the API key from localStorage.
 * If an API key is found, it is populated in the input field.
 */
window.onload = function () {
    // Retrieve the stored API key from localStorage
    document.getElementById('apiKey').value = getApiKey();
};

/**
 * Function to check the health status of the API on window load.
 * Updates the 'checkHealth' element with the status of the service.
 */
window.onload = async function checkHealth() {
    const responseContainer = document.getElementById('checkHealth');
    responseContainer.textContent = 'Checking API status...';

    const apiKey = getApiKey();  // Retrieve the saved API key
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

// Main transcription function
async function requestTranscription() {
    const responseContainer = document.getElementById('response');
    const apiKey = getApiKey();

    // Guard clauses for early exit
    if (!selectedFile) {
        return displayError(apiResponse, ERROR_MESSAGES.NO_FILE);
    }
    if (!apiKey) {
        return displayError(apiResponse, ERROR_MESSAGES.MISSING_API_KEY);
    }

    apiResponse.textContent = 'Calling API...';

    try {
        const formData = createFormData(selectedFile);
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {'Authorization': apiKey},
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        responseContainer.textContent = JSON.stringify(data, null, 2);
        transcriptionFileName.textContent = "File name: " + selectedFile.name;

        // Delegate transcription ID handling to the appropriate function
        requestTranscriptionText(data['transcription_id']);
    } catch (error) {
        displayError(responseContainer, ERROR_MESSAGES.INVALID_API_KEY);
    }
}

function requestTranscriptionText(transcription_id) {

    const apiKey = localStorage.getItem('apiKey');
    const HEADERS = {
        'Authorization': `${apiKey}`,
    };

    loadingContainer.innerHTML = loadingSVG;

    /**
     * Handles the response data from the fetch request
     * @param {Object} transcriptionData - The data returned from the API
     */
    const handleResponse = (transcriptionData) => {
        if (transcriptionData.status === 'finished') {
            loadingContainer.innerHTML = "";
            responseTextContainer.textContent = JSON.stringify(transcriptionData.transcript.text, null, 2)
            clearInterval(timer);
        } else if (transcriptionData.status === 'failed') {
            loadingContainer.innerHTML = "";
            responseTextContainer.textContent = 'Transcription failed';
            clearInterval(timer);
        } else if (transcriptionData.status === 'in_query') {
            responseTextContainer.textContent = 'Transcription in progress';
        }
    };

    function pollTranscription(transcription_id) {
        fetch(`${API_URL}${transcription_id}`, {
            method: 'GET',
            headers: HEADERS,
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                return response.json();
            })
            .then(transcriptionData => {
                handleResponse(transcriptionData);
            })
            .catch(error => {
                clearInterval(timer);
                responseTextContainer.textContent = 'Transcription failed';
                console.log('Error:', error);
            });
    }

    const timer = setInterval(() => pollTranscription(transcription_id), 1000);
}

async function requestTranslation() {

    const apiKey = getApiKey();

    // Guard clauses for early exit
    if (!selectedFile) {
        return displayError(responseContainer, ERROR_MESSAGES.NO_FILE);
    }
    if (!apiKey) {
        return displayError(responseContainer, ERROR_MESSAGES.MISSING_API_KEY);
    }

    responseContainer.textContent = 'Calling API...';

    try {
        const formData = createFormData(selectedFile);
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {'Authorization': apiKey},
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        responseContainer.textContent = JSON.stringify(data, null, 2);
        transcriptionFileName.textContent = "File name: " + selectedFile.name;

        // Delegate transcription ID handling to the appropriate function
        requestTranscriptionText(data['transcription_id']);
    } catch (error) {
        displayError(responseContainer, ERROR_MESSAGES.INVALID_API_KEY);
    }
}

function requestTranslationText() {

    const apiKey = localStorage.getItem('apiKey');
    const HEADERS = {
        'Authorization': `${apiKey}`,
    };

    loadingContainer.innerHTML = loadingSVG;

    /**
     * Handles the response data from the fetch request
     * @param {Object} translationData - The data returned from the API
     */
    const handleResponse = (translationData) => {
        if (translationData.status === 'finished') {
            loadingContainer.innerHTML = "";
            responseTextContainer.textContent = JSON.stringify(translationData.transcript.text, null, 2)
            clearInterval(timer);
        } else if (translationData.status === 'failed') {
            loadingContainer.innerHTML = "";
            responseTextContainer.textContent = 'Transcription failed';
            clearInterval(timer);
        } else if (translationData.status === 'in_query') {
            responseTextContainer.textContent = 'Transcription in progress';
        }
    }

    function pollTranslation(transcription_id) {
        fetch(`${API_URL}${transcription_id}`, {
            method: 'GET',
            headers: HEADERS,
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                return response.json();
            })
            .then(transcriptionData => {
                handleResponse(transcriptionData);
            })
            .catch(error => {
                clearInterval(timer);
                responseTextContainer.textContent = 'Transcription failed';
                console.log('Error:', error);
            });
    }

    const timer = setInterval(() => pollTranscription(transcription_id), 1000);

}