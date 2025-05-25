document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageContent = document.getElementById('message-content');
    const chatContainer = document.getElementById('chat-container');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    // Scroll to bottom on load
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Mark unread messages as read
    document.querySelectorAll('.message .unread-tag').forEach(tag => {
        const messageId = tag.closest('.message').dataset.messageId;
        fetch(`/messages/mark_read/${messageId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
        }).then(() => tag.remove());
    });

    if (messageForm) {
        messageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = messageContent.value.trim();
            if (!content) return;

            try {
                const response = await fetch('/messages/send/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        receiver_id: messageForm.receiver_id.value,
                        content: content
                    }),
                });

                const result = await response.json();
                if (result.status === 'success') {
                    appendNewMessage(result.message);
                    messageContent.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else {
                    alert(`Error: ${result.message}`);
                }
            } catch (error) {
                alert('Failed to send message.');
            }
        });
    }

    function appendNewMessage(message) {
        const isSender = message.sender_id == userId;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message mb-4 ${isSender ? 'sent' : 'received'}`;
        messageDiv.dataset.messageId = message.message_id;
        
        messageDiv.innerHTML = `
            <div class="flex ${isSender ? 'justify-end' : 'justify-start'} items-center space-x-2">
                ${!isSender ? `<img src="${message.receiver_picture_url || defaultAvatar}" class="w-8 h-8 rounded-full">` : ''}
                <div class="max-w-xs p-3 rounded-lg ${isSender ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}">
                    <p class="text-sm">${message.content}</p>
                    <p class="text-xs mt-1 opacity-75">${formatDate(message.sent_at)}</p>
                </div>
                ${isSender ? `<img src="${message.sender_picture_url || defaultAvatar}" class="w-8 h-8 rounded-full">` : ''}
            </div>
        `;
        chatContainer.appendChild(messageDiv);
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }
});