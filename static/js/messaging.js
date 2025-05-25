document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageContent = document.getElementById('message-content');
    const chatContainer = document.getElementById('chat-container');

    // Get CSRF token from form input
    function getCsrfToken() {
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return tokenInput ? tokenInput.value : '';
    }

    // Scroll to the bottom of chat container on page load
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Mark unread messages as read on page load
    const unreadMessages = document.querySelectorAll('.message .unread-tag');
    unreadMessages.forEach(tag => {
        const messageDiv = tag.closest('.message');
        const messageId = messageDiv.getAttribute('data-message-id');

        fetch(`/messaging/read/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                tag.remove();
            } else {
                console.error('Failed to mark message as read:', result.message);
            }
        })
        .catch(error => console.error('Error marking message as read:', error));
    });

    // Handle message form submission
    if (messageForm) {
        messageForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const receiverId = messageForm.querySelector('input[name="receiver_id"]').value;
            const content = messageContent.value.trim();
            const userId = messageForm.dataset.userId;
            const receiverPictureUrl = messageForm.dataset.receiverPicture || '';
            const defaultAvatar = messageForm.dataset.defaultAvatar;

            if (!content) {
                alert('Please enter a message.');
                return;
            }

            try {
                const response = await fetch('/messaging/send/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ receiver_id: receiverId, content: content }),
                });

                const result = await response.json();
                if (result.status === 'success') {
                    const newMessage = result.message;
                    const isSender = newMessage.sender_id == userId;
                    const senderAvatar = isSender ? (newMessage.sender_picture_url || defaultAvatar) : (receiverPictureUrl || defaultAvatar);
                    const receiverAvatar = !isSender ? (newMessage.sender_picture_url || defaultAvatar) : (receiverPictureUrl || defaultAvatar);

                    const newMessageDiv = document.createElement('div');
                    newMessageDiv.className = `message mb-4 animate-fadeIn ${isSender ? 'sent' : 'received'}`;
                    newMessageDiv.setAttribute('data-message-id', newMessage.message_id);
                    newMessageDiv.innerHTML = `
                        <div class="flex ${isSender ? 'justify-end' : 'justify-start'} items-center space-x-2">
                            ${!isSender ? `<img src="${receiverAvatar}" alt="Receiver Avatar" class="w-8 h-8 rounded-full">` : ''}
                            <div class="max-w-xs p-3 rounded-lg ${isSender ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}">
                                <p class="text-sm">${newMessage.content}</p>
                                <p class="text-xs mt-1 opacity-75">${new Date(newMessage.sent_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })}</p>
                            </div>
                            ${isSender ? `<img src="${senderAvatar}" alt="Your Avatar" class="w-8 h-8 rounded-full">` : ''}
                        </div>
                    `;
                    chatContainer.appendChild(newMessageDiv);
                    messageContent.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else {
                    alert(`Error: ${result.message}`);
                }
            } catch (error) {
                console.error('Error sending message:', error);
                alert('Failed to send message. Check console for details.');
            }
        });
    }
});