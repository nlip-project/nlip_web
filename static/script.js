import { NLIP_FACTORY } from './nlip.js';

const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  const pair = document.createElement('div');
  pair.className = 'message-pair';

  const userBubble = document.createElement('div');
  userBubble.className = 'user-bubble';
  userBubble.textContent = message;
  pair.appendChild(userBubble);

  const botBox = document.createElement('div');
  botBox.className = 'bot-box';
  botBox.textContent = '...'; // Placeholder while waiting
  pair.appendChild(botBox);

  chatBox.appendChild(pair);
  chatBox.scrollTop = chatBox.scrollHeight;

  const nlipMessage = NLIP_FACTORY.create_text("text", "English", message);



  input.value = '';

  try {
    const response = await fetch('/nlip/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: nlipMessage.jsonSerialize()
    });

    const data = await response.json();
    botBox.textContent =  data.content || 'No response';
  } catch (error) {
        botBox.textContent = 'Error connecting to chat engine.';
    console.error(error);
  }
});

