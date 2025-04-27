class ChatManager {
    constructor() {
        this.chatDiv = document.getElementById('chatbot-response');
        this.inputField = document.getElementById('chatbot-question');
        this.sendButton = document.getElementById('chatbot-send');
        this.initialize();
    }

    initialize() {
        this.addMessage('bot', 'How can I help you today?');
        this.setupEventListener();
        this.setupWebSocket();
    }

    setupEventListener() {
        this.sendButton.addEventListener('click', () => this.handleSendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSendMessage();
            }
        });
    }

    setupWebSocket() {
        this.ws = new WebSocket('ws://localhost:5000/chat');
        
        this.ws.onopen = () => {
            console.log('Connected to WebSocket server');
            this.addMessage('bot', 'Connected to real-time chat server');
        };
        
        this.ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.type === 'message') {
                this.addMessage('bot', response.data);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage('bot', 'Sorry, real-time connection is lost. Please try again.');
        };
    }

    handleSendMessage() {
        const message = this.inputField.value.trim();
        if (message) {
            this.addMessage('user', message);
            this.processUserMessage(message);
            this.clearInput();
        }
    }

    async processUserMessage(message) {
        try {
            // Send message to WebSocket server
            await this.ws.send(JSON.stringify({ 
                type: 'message',
                data: message
            }));
            
            // Simulate API call fallback
            const response = await new Promise(resolve => setTimeout(resolve, 1000));
            this.addMessage('bot', response);
        } catch (error) {
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            console.error('Error processing message:', error);
        }
    }

    async getBotResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error getting bot response:', error);
            throw error;
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-container chat-${sender}`;
        messageDiv.innerHTML = `
            <div class="chat-message chat-${sender}">
                <span class="chat-text">${text}</span>
            </div>
        `;
        this.chatDiv.appendChild(messageDiv);
        this.chatDiv.scrollTop = this.chatDiv.scrollHeight;
        
        // Add typing indicator
        if (sender === 'bot') {
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'typing-indicator';
            typingIndicator.textContent = 'AI is typing...';
            messageDiv.appendChild(typingIndicator);
        }
    }

    clearInput() {
        this.inputField.value = '';
        this.inputField.focus();
    }
}

// Initialize chat manager when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
});
