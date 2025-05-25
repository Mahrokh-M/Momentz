document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageContent = document.getElementById('message-content');
    const chatContainer = document.getElementById('chat-container');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const userId = document.querySelector('meta[name="user-id"]').content; // Changed this line
    const defaultAvatar = document.querySelector('meta[name="default-avatar"]').content; // Changed this line

    // Scroll to bottom on load
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    if (messageForm) {
        messageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = messageContent.value.trim();
            if (!content) return;

            // Disable button during request
            const submitBtn = messageForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';

            try {
                const response = await fetch('/messages/send/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        receiver_id: messageForm.querySelector('input[name="receiver_id"]').value,
                        content: content
                    }),
                });

                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.message || 'Failed to send message');
                }

                if (result.status === 'success') {
                    appendNewMessage(result.message);
                    messageContent.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else {
                    throw new Error(result.message || 'Unknown error occurred');
                }
            } catch (error) {
                console.error('Error:', error);
                showTempMessage(`Error: ${error.message}`, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    function appendNewMessage(message) {
        if (!chatContainer) return;
        
        const isSender = parseInt(message.sender_id) === parseInt(userId);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message mb-4 ${isSender ? 'sent' : 'received'}`;
        messageDiv.dataset.messageId = message.message_id;
        
        const avatarUrl = isSender ? 
            (message.sender_picture_url || defaultAvatar) : 
            (message.receiver_picture_url || defaultAvatar);
        
        messageDiv.innerHTML = `
            <div class="flex ${isSender ? 'justify-end' : 'justify-start'} items-center space-x-2">
                ${!isSender ? `<img src="${avatarUrl}" class="w-8 h-8 rounded-full border border-neon-cyan">` : ''}
                <div class="max-w-xs p-3 rounded-lg ${isSender ? 'bg-cyan-900 text-neon-cyan border border-neon-cyan' : 'bg-gray-900 text-neon-pink border border-neon-purple'}">
                    <p class="text-sm">${message.content}</p>
                    <p class="text-xs mt-1 ${isSender ? 'text-neon-cyan' : 'text-neon-purple'}">${formatDate(message.sent_at)}</p>
                </div>
                ${isSender ? `<img src="${avatarUrl}" class="w-8 h-8 rounded-full border border-neon-purple">` : ''}
            </div>
        `;
        chatContainer.appendChild(messageDiv);
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    function showTempMessage(text, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} position-fixed top-20 end-20 z-50`;
        alert.style.cssText = 'min-width: 300px; animation: fadeIn 0.3s ease-out;';
        alert.innerHTML = `
            ${text}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }
});