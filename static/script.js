const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatWindow = document.getElementById('chatWindow');
const typingIndicator = document.getElementById('typingIndicator');

// chat window me UI message load handler logic
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const now = new Date();
    const timeStr = now.getHours() + ':' + now.getMinutes().toString().padStart(2, '0');

    messageDiv.innerHTML = `
        <div class="message-content">${text}</div>
        <div class="timestamp">${timeStr}</div>
    `;
    
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// chat submit handling listener trigger function
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    addMessage(question, 'user');
    userInput.value = '';
    
    typingIndicator.style.display = 'flex';

    try {
        // flask route endpoint execution trigger
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();
        
        typingIndicator.style.display = 'none';

        if (data.answer) {
            addMessage(data.answer, 'system');
        } else {
            addMessage('Error: ' + (data.error || 'Unknown error'), 'system');
        }
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage('Error connecting to server.', 'system');
        console.error('Fetch error:', error);
    }
});
