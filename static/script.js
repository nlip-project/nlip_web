import { NLIP_Factory} from './nlip.js'

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
    const fileObj = file.files[0];
    const reader = await new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onload = () => resolve(r);
      r.onerror = reject;
      r.readAsDataURL(fileObj);
    });
    // Extract base64 string from data URL
    const base64 = reader.result.split(',')[1];
    nlipMessage.addImage(base64, "png");
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

