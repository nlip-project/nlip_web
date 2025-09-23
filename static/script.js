import { NLIP_Factory} from './save/script.js'

const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const file = document.getElementById('file-input');
const chatBox = document.getElementById('chat-box');

file.addEventListener('change', () => {
  const fileList = document.getElementById('file-list');
  fileList.innerHTML = '';
  Array.from(file.files).forEach(f => {
    const li = document.createElement('li');
    li.textContent = f.name;
    fileList.appendChild(li);
  });
});


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

  const nlipMessage = NLIP_Factory.createText(message);

  if (file.files.length > 0) {
    const fileData = file.files[0];
    nlipMessage.addImage(fileData, "png");
  }

  input.value = '';

  try {
    const response = await fetch('/nlip/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: nlipMessage.toJSON()
    });

    const data = await response.json();
    botBox.textContent =  data.content || 'No response';
  } catch (error) {
        botBox.textContent = 'Error connecting to chat engine.';
    console.error(error);
  }
});

