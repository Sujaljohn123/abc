const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatLog = document.getElementById('chat-log');

sendBtn.addEventListener('click', () => {
  const userQuery = userInput.value.trim();
  if (userQuery !== '') {
    // Send request to backend API
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: userQuery }),
    })
      .then(response => response.json())
      .then(data => {
        // Update chat log with response
        chatLog.innerHTML += `<p>AI: ${data.response}</p>`;
        userInput.value = '';
      })
      .catch(error => console.error('Error:', error));
  }
});
