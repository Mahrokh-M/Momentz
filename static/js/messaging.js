document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageContent = document.getElementById('message-content');
    const chatContainer = document.getElementById('chat-container');

    // Scroll to the bottom of chat container on page load
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Mark unread messages as read on page load
    const unreadMessages = document.querySelectorAll('.message .unread-tag');
    unreadMessages.forEach(tag => {
        const messageDiv = tag.closest('.message');
        const messageId = messageDiv.getAttribute('data-message-id');
        
        fetch(`/messages/mark_read/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf-token'),
            },
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'success') {
                tag.remove(); // Remove the "Unread" tag from the UI
            } else {
                console.error('Failed to mark message as read:', result.message);
            }
        })
        .catch(error => console.error('Error marking message as read:', error));
    });

    if (messageForm) {
        messageForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const receiverId = messageForm.querySelector('input[name="receiver_id"]').value;
            const content = messageContent.value.trim();

            if (content) {
                console.log('Sending message:', { receiverId, content });
                try {
                    const response = await fetch('/messages/send/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrf-token'),
                        },
                        body: JSON.stringify({ receiver_id: receiverId, content: content }),
                    });

                    const result = await response.json();
                    console.log('Server response:', result);

                    if (result.status === 'success') {
                        const newMessage = result.message;
                        const isSender = newMessage.sender_id == userId;
                        const receiverPictureUrl = "{{ receiver_picture_url|default_if_none:'' }}";
                        const senderAvatar = isSender ? (newMessage.sender_picture_url || defaultAvatar) : (receiverPictureUrl || defaultAvatar);
                        const receiverAvatar = !isSender ? (newMessage.sender_picture_url || defaultAvatar) : (receiverPictureUrl || defaultAvatar);
                        console.log("Sender Avatar:", senderAvatar);
                        console.log("Receiver Avatar:", receiverAvatar);
                        const newMessageDiv = document.createElement('div');
                        newMessageDiv.className = 'message mb-4 animate-fadeIn';
                        newMessageDiv.innerHTML = `
                            <div class="flex ${isSender ? 'justify-end' : 'justify-start'} items-center space-x-2">
                                ${isSender ? '' : `<img src="${receiverAvatar}" alt="Receiver Avatar" class="w-8 h-8 rounded-full">`}
                                <div class="max-w-xs p-3 rounded-lg ${isSender ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}">
                                    <p class="text-sm">${newMessage.content}</p>
                                    <p class="text-xs mt-1 opacity-75">${new Date(newMessage.sent_at).toLocaleString()}</p>
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
                    console.error('Fetch error:', error);
                    alert('Failed to send message. Check console for details.');
                }
            }
        });
    }

    function getCookie(name) {
        let cookieValue = document.querySelector(`meta[name="${name}"]`)?.content;
        if (!cookieValue && document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});