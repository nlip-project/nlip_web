// Page 3: Text & Image Chat Script - Text and image upload with text response
// ---- Helpers ---------------------------------------------------------------
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));
const el = (tag, cls) => { const n=document.createElement(tag); if (cls) n.className=cls; return n; };

const CHAT_KEY = 'nlip_text_image_chat_history_v1';
const THEME_KEY = 'nlip_theme';
const NAME_KEY  = 'nlip_display_name';

// ---- State -----------------------------------------------------------------
let chats = loadChats();      // {id, title, messages:[{role, text, attachments?}]}
let currentId = chats[0]?.id || newChat();
let typingEl;
let pendingAttachments = [];

// ---- Theme (data-theme on <html>) -----------------------------------------
function applyTheme(pref){
  const root = document.documentElement;
  const set = (mode) => root.setAttribute('data-theme', mode);
  if (pref === 'auto'){
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    set(dark ? 'dark' : 'light');
  } else {
    set(pref);
  }
  localStorage.setItem(THEME_KEY, pref);
}
applyTheme(localStorage.getItem(THEME_KEY) || 'light');

// quick toggle button in sidebar
$('#themeToggle').addEventListener('click', () => {
  const cur = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(cur === 'dark' ? 'light' : 'dark');
});

// ---- Settings modal --------------------------------------------------------
const settings = $('#settingsModal');
$('#settingsBtn').onclick = () => settings.showModal();
$('#nameInput').value = localStorage.getItem(NAME_KEY) || 'User';
$('#nameInput').addEventListener('input', e => {
  localStorage.setItem(NAME_KEY, e.target.value);
  $('#userName').textContent = e.target.value || 'User';
});
$('#userName').textContent = $('#nameInput').value;
$$('.seg button').forEach(b => b.onclick = () => applyTheme(b.dataset.theme));

// ---- History ---------------------------------------------------------------
function loadChats(){
  try { return JSON.parse(localStorage.getItem(CHAT_KEY)) || []; }
  catch { return []; }
}
function saveChats(){
  localStorage.setItem(CHAT_KEY, JSON.stringify(chats));
}
function newChat(){
  const id = 'c_'+Date.now();
  chats.unshift({ id, title:'New chat', messages:[] });
  saveChats();
  renderHistory();
  setActive(id);
  clearFeed();
  return id;
}
function setActive(id){
  currentId = id;
  $$('#historyList .item').forEach(n => n.classList.toggle('active', n.dataset.id===id));
  clearFeed();
  (chats.find(c=>c.id===id)?.messages || []).forEach(m=>renderMessage(m.role, m.text, m.attachments));
}
function renderHistory(){
  const wrap = $('#historyList');
  wrap.innerHTML = '';
  if (chats.length===0){
    wrap.innerHTML = '<p class="sub">No conversations yet.</p>';
    return;
  }
  chats.forEach(c=>{
    const row = el('div','item'); row.dataset.id = c.id;
    const titleBtn = el('button','title'); titleBtn.type = 'button';
    titleBtn.textContent = c.title || 'New chat';
    const del = el('button','del'); del.type = 'button'; del.title = 'Delete chat';
    del.textContent = '🗑';
    row.append(titleBtn, del);
    if (c.id===currentId) row.classList.add('active');
    wrap.appendChild(row);
  });
}
$('#newChatBtn').onclick = newChat;

// click handling for history: select or delete
$('#historyList').addEventListener('click', (e) => {
  const item = e.target.closest('.item');
  if (!item) return;
  const id = item.dataset.id;

  if (e.target.classList.contains('del')){
    const title = chats.find(c=>c.id===id)?.title || 'this chat';
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;
    chats = chats.filter(c => c.id !== id);
    saveChats();
    if (currentId === id){
      currentId = chats[0]?.id || newChat();
    }
    renderHistory();
    setActive(currentId);
    return;
  }
  if (e.target.classList.contains('title')) {
    setActive(id);
  }
});

// ---- File Attachment Handling ---------------------------------------------
function fileToDataURL(file){
  return new Promise(res=>{
    const r=new FileReader();
    r.onload=()=>res(r.result);
    r.readAsDataURL(file);
  });
}

function updateAttachmentPreview() {
  const preview = $('#attachment-preview');
  preview.innerHTML = '';
  
  if (pendingAttachments.length === 0) {
    preview.style.display = 'none';
    return;
  }
  
  preview.style.display = 'flex';
  
  pendingAttachments.forEach((att, index) => {
    const item = el('div', 'attachment-item');
    
    if (att.preview) {
      const img = el('img', 'attachment-image');
      img.src = att.preview;
      img.alt = att.name;
      item.appendChild(img);
    } else {
      const icon = el('span');
      icon.textContent = '📎';
      item.appendChild(icon);
    }
    
    const name = el('span', 'attachment-name');
    name.textContent = att.name;
    item.appendChild(name);
    
    const remove = el('button', 'attachment-remove');
    remove.textContent = '×';
    remove.onclick = () => {
      pendingAttachments.splice(index, 1);
      updateAttachmentPreview();
    };
    item.appendChild(remove);
    
    preview.appendChild(item);
  });
}

$('#fileInput').addEventListener('change', async (e) => {
  pendingAttachments = [];
  const files = Array.from(e.target.files || []);
  
  for (const f of files) {
    const att = { name: f.name, size: f.size, type: f.type, file: f };
    if (f.type.startsWith('image/')) {
      att.preview = await fileToDataURL(f);
    }
    pendingAttachments.push(att);
  }
  
  updateAttachmentPreview();
});

// ---- Chat feed -------------------------------------------------------------
function clearFeed(){ $('#chat-box').innerHTML=''; }
function renderMessage(role, text, attachments){
  const g = el('div','msg-group '+(role==='user'?'user':''));
  const a = el('div','avatar'); a.textContent = role==='user'?'You':'AI';
  const bWrap = el('div','bubbles');
  
  // Add text content
  if (text) {
    const b = el('div','bubble'); b.textContent = text;
    bWrap.appendChild(b);
  }

  // Add attachments if present
  if (attachments && attachments.length){
    attachments.forEach(att=>{
      if (att.preview && att.type?.startsWith('image/')){
        const img = new Image(); 
        img.src = att.preview; 
        img.alt = att.name; 
        img.className='bubble';
        img.style.maxWidth='220px'; 
        img.style.borderRadius='12px';
        img.style.marginTop = '8px';
        bWrap.appendChild(img);
      } else {
        const note = el('div','bubble'); 
        note.textContent = `📎 ${att.name} (${Math.round(att.size/1024)} KB)`;
        note.style.marginTop = '8px';
        bWrap.appendChild(note);
      }
    });
  }

  g.append(a,bWrap);
  $('#chat-box').appendChild(g);
  $('#chat-box').scrollTop = $('#chat-box').scrollHeight;
}
function typing(on){
  if (on){
    typingEl = el('div','msg-group');
    const a = el('div','avatar'); a.textContent='AI';
    const b = el('div','bubble'); b.innerHTML = `<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
    const w = el('div','bubbles'); w.appendChild(b);
    typingEl.append(a,w); $('#chat-box').appendChild(typingEl);
    $('#chat-box').scrollTop = $('#chat-box').scrollHeight;
  } else if (typingEl){ typingEl.remove(); typingEl = null; }
}

// ---- Suggestions (auto-fill + focus) --------------------------------------
$('#chips').addEventListener('click', (e)=>{
  const chip = e.target.closest('.chip');
  if (!chip) return;
  $('#user-input').value = chip.textContent.trim();
  $('#user-input').dispatchEvent(new Event('input'));
  $('#user-input').focus();
});

// ---- Send flow -------------------------------------------------------------
const form  = $('#chat-form');
const input = $('#user-input');
const send  = $('#send');

input.addEventListener('input', ()=>{
  send.disabled = input.value.trim().length===0 && pendingAttachments.length === 0;
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 160) + 'px';
});
input.addEventListener('keydown', (e)=>{
  if (e.key==='Enter' && !e.shiftKey){
    e.preventDefault();
    if (!send.disabled) form.requestSubmit();
  }
});
$('#clearBtn').onclick = () => { chats.find(c=>c.id===currentId).messages=[]; saveChats(); clearFeed(); };

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const text = input.value.trim();
  if (!text && pendingAttachments.length === 0) return;

  const chat = chats.find(c=>c.id===currentId);
  if (chat.messages.length===0) {
    chat.title = text.slice(0,40) || 'Image chat';
  }

  const attachments = [...pendingAttachments];
  
  // Add user message to chat
  renderMessage('user', text, attachments);
  chat.messages.push({ role:'user', text, attachments });
  saveChats();

  input.value=''; 
  input.dispatchEvent(new Event('input'));
  
  // Clear attachments
  pendingAttachments = [];
  updateAttachmentPreview();
  $('#fileInput').value = '';
  
  typing(true);

  try{
    const nlipMessage = {
      messagetype: "text",
      format: "text",
      subformat: "English",
      content: text || "Image analysis request",
      images: attachments?.filter(a => a.type?.startsWith('image/')).map(a => a.preview) || []
    };

    const res = await fetch('/nlip/', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify(nlipMessage)
    });
    const data = await res.json();
    typing(false);
    const reply = (data && (data.content || data.message || data.reply)) || 'No response';
    renderMessage('assistant', reply);
    chat.messages.push({ role:'assistant', text: reply });
    saveChats();
  }catch(err){
    typing(false);
    renderMessage('assistant', '⚠️ Error connecting to chat engine.');
    console.error(err);
  }
});

// initial paint
renderHistory();
setActive(currentId);
