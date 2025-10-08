// ---- Helpers ---------------------------------------------------------------
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));
const el = (tag, cls) => { const n=document.createElement(tag); if (cls) n.className=cls; return n; };

const CHAT_KEY = 'nlip_chat_history_v1';
const THEME_KEY = 'nlip_theme';
const NAME_KEY  = 'nlip_display_name';

// ---- State -----------------------------------------------------------------
let chats = loadChats();      // {id, title, messages:[{role, text, attachments?}]}
let currentId = chats[0]?.id || newChat();
let typingEl;

// ---- Theme -----------------------------------------------------------------
function applyTheme(pref){
  const root = document.documentElement;
  root.classList.remove('dark');
  if (pref === 'dark' || (pref==='auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)){
    root.classList.add('dark');
  }
  localStorage.setItem(THEME_KEY, pref);
}
applyTheme(localStorage.getItem(THEME_KEY) || 'auto');

$('#themeToggle').addEventListener('click', () => {
  const cur = localStorage.getItem(THEME_KEY) || 'auto';
  applyTheme(cur === 'dark' ? 'light' : 'dark');
});

// ---- Settings modal --------------------------------------------------------
const settings = $('#settingsModal');
$('#settingsBtn').onclick = () => settings.showModal();
$('#nameInput').value = localStorage.getItem(NAME_KEY) || 'User';
$('#nameInput').addEventListener('input', e => localStorage.setItem(NAME_KEY, e.target.value));
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
  $$('#historyList button').forEach(b=>b.classList.toggle('active', b.dataset.id===id));
  clearFeed();
  (chats.find(c=>c.id===id)?.messages || []).forEach(m=>renderMessage(m.role, m.text, m.attachments));
}
function renderHistory(){
  const wrap = $('#historyList');
  wrap.innerHTML = '';
  if (chats.length===0){ wrap.innerHTML = '<p class="muted">No conversations yet.</p>'; return; }
  chats.forEach(c=>{
    const btn = el('button');
    btn.dataset.id = c.id;
    btn.textContent = c.title;
    btn.onclick = () => setActive(c.id);
    if (c.id===currentId) btn.classList.add('active');
    wrap.appendChild(btn);
  });
}
$('#newChatBtn').onclick = newChat;

// ---- Chat feed -------------------------------------------------------------
function clearFeed(){ $('#chat-box').innerHTML=''; }
function renderMessage(role, text, attachments){
  const g = el('div','msg-group '+(role==='user'?'user':''));
  const a = el('div','avatar'); a.textContent = role==='user'?'You':'AI';
  const bWrap = el('div','bubbles');
  const b = el('div','bubble'); b.textContent = text;
  bWrap.appendChild(b);

  if (attachments && attachments.length){
    attachments.forEach(att=>{
      if (att.type.startsWith('image/')){
        const img = new Image(); img.src = att.preview; img.alt = att.name; img.className='bubble';
        img.style.maxWidth='220px'; img.style.borderRadius='12px';
        bWrap.appendChild(img);
      } else {
        const note = el('div','bubble'); note.textContent = `Attached: ${att.name} (${Math.round(att.size/1024)} KB)`;
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

// ---- Suggestions -----------------------------------------------------------
$('#chips').addEventListener('click', e=>{
  if (e.target.classList.contains('chip')){
    $('#user-input').value = e.target.textContent;
    $('#user-input').dispatchEvent(new Event('input'));
    $('#user-input').focus();
  }
});

// ---- Attachments -----------------------------------------------------------
let pendingAttachments = [];
$('#fileInput').addEventListener('change', async (e)=>{
  pendingAttachments = [];
  const files = Array.from(e.target.files||[]);
  for (const f of files){
    const att = { name:f.name, size:f.size, type:f.type };
    if (f.type.startsWith('image/')){
      att.preview = await fileToDataURL(f);
    }
    pendingAttachments.push(att);
  }
  // show a subtle toast by adding a hint bubble
  if (pendingAttachments.length){
    renderMessage('user', '(attachment ready: will send with your next message)', pendingAttachments);
  }
});
function fileToDataURL(file){
  return new Promise(res=>{
    const r=new FileReader();
    r.onload=()=>res(r.result);
    r.readAsDataURL(file);
  });
}

// ---- Send flow -------------------------------------------------------------
const form  = $('#chat-form');
const input = $('#user-input');
const send  = $('#send');

input.addEventListener('input', ()=>{
  send.disabled = input.value.trim().length===0;
  // grow textarea
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
  if (!text) return;

  // update title if first message
  const chat = chats.find(c=>c.id===currentId);
  if (chat.messages.length===0) chat.title = text.slice(0,40);

  // optimistic render
  const attachments = pendingAttachments; // copy
  renderMessage('user', text, attachments);
  chat.messages.push({ role:'user', text, attachments });
  saveChats();
  pendingAttachments = [];
  $('#fileInput').value = '';

  // payload to your existing NLIP echo endpoint (text only so we keep compatibility)
  const nlipMessage = {
    messagetype: "text",
    format: "text",
    subformat: "English",
    content: attachments?.length ? `${text}\n\n[User attached: ${attachments.map(a=>a.name).join(', ')}]` : text
  };

  input.value=''; input.dispatchEvent(new Event('input'));
  typing(true);

  try{
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

// ---------------------------------------------------------------------------
