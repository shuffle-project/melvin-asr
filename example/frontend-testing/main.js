// Select elements
const toggleSwitch = document.getElementById('toggleSwitch');
const restContent = document.getElementById('restContent');
const websocketContent = document.getElementById('websocketContent');

// Toggle content based on the switch state
toggleSwitch.addEventListener('change', () => {
    if (toggleSwitch.checked) {
        // Show WebSocket content, hide REST content
        restContent.classList.remove('active');
        websocketContent.classList.add('active');
    } else {
        // Show REST content, hide WebSocket content
        websocketContent.classList.remove('active');
        restContent.classList.add('active');
    }
});
