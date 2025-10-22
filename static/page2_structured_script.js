// Page 2: Structured Chat Script - Text input with structured HTML response (products/tables)
// ---- Helpers ---------------------------------------------------------------
const $ = sel => document.querySelector(sel);
const $$ = sel => Array.from(document.querySelectorAll(sel));
const el = (tag, cls) => { const n=document.createElement(tag); if (cls) n.className=cls; return n; };

const CHAT_KEY = 'nlip_structured_chat_history_v1';
const THEME_KEY = 'nlip_theme';
const NAME_KEY  = 'nlip_display_name';

// ---- State -----------------------------------------------------------------
let chats = loadChats();      // {id, title, messages:[{role, text, structured?}]}
let currentId = chats[0]?.id || newChat();
let typingEl;

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
  (chats.find(c=>c.id===id)?.messages || []).forEach(m=>renderMessage(m.role, m.text, m.structured));
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

// ---- Structured Content Rendering -----------------------------------------
function renderStructuredContent(content) {
  try {
    // Try to parse as JSON first
    const data = JSON.parse(content);
    
    if (Array.isArray(data) && data.length > 0) {
      // Check if it looks like product data
      if (data[0].name || data[0].title || data[0].product) {
        return renderProductTable(data);
      } else {
        // Generic table
        return renderGenericTable(data);
      }
    } else if (typeof data === 'object' && data !== null) {
      // Single product card
      return renderProductCard(data);
    }
  } catch (e) {
    // If not JSON, try to detect HTML-like structure
    if (content.includes('<table>') || content.includes('<tr>')) {
      return renderHTMLTable(content);
    }
  }
  
  // Fallback: render as plain text
  return renderPlainText(content);
}

function renderProductTable(products) {
  const container = el('div', 'structured-response');
  
  const table = el('table', 'product-table');
  
  // Create header
  const thead = el('thead');
  const headerRow = el('tr');
  
  // Define common product fields
  const headers = ['Name', 'Price', 'Description', 'Category', 'Link'];
  headers.forEach(header => {
    const th = el('th');
    th.textContent = header;
    headerRow.appendChild(th);
  });
  
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  // Create body
  const tbody = el('tbody');
  products.forEach(product => {
    const row = el('tr');
    
    // Name
    const nameCell = el('td');
    nameCell.textContent = product.name || product.title || product.product || 'N/A';
    row.appendChild(nameCell);
    
    // Price
    const priceCell = el('td');
    priceCell.textContent = product.price || product.cost || 'N/A';
    row.appendChild(priceCell);
    
    // Description
    const descCell = el('td');
    descCell.textContent = product.description || product.desc || 'N/A';
    row.appendChild(descCell);
    
    // Category
    const catCell = el('td');
    catCell.textContent = product.category || product.type || 'N/A';
    row.appendChild(catCell);
    
    // Link
    const linkCell = el('td');
    if (product.link || product.url) {
      const link = el('a', 'product-link');
      link.href = product.link || product.url;
      link.textContent = 'View';
      link.target = '_blank';
      linkCell.appendChild(link);
    } else {
      linkCell.textContent = 'N/A';
    }
    row.appendChild(linkCell);
    
    tbody.appendChild(row);
  });
  
  table.appendChild(tbody);
  container.appendChild(table);
  return container;
}

function renderGenericTable(data) {
  const container = el('div', 'structured-response');
  const table = el('table', 'product-table');
  
  if (Array.isArray(data) && data.length > 0) {
    // Create header
    const thead = el('thead');
    const headerRow = el('tr');
    
    const headers = Object.keys(data[0]);
    headers.forEach(header => {
      const th = el('th');
      th.textContent = header.charAt(0).toUpperCase() + header.slice(1);
      headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = el('tbody');
    data.forEach(item => {
      const row = el('tr');
      headers.forEach(header => {
        const td = el('td');
        td.textContent = item[header] || '';
        row.appendChild(td);
      });
      tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
  }
  
  container.appendChild(table);
  return container;
}

function renderProductCard(product) {
  const container = el('div', 'structured-response');
  const card = el('div', 'product-card');
  
  if (product.image || product.img) {
    const img = el('img', 'product-image');
    img.src = product.image || product.img;
    img.alt = product.name || product.title || 'Product';
    card.appendChild(img);
  }
  
  const info = el('div', 'product-info');
  
  if (product.name || product.title) {
    const title = el('h3', 'product-title');
    title.textContent = product.name || product.title;
    info.appendChild(title);
  }
  
  if (product.description || product.desc) {
    const desc = el('p', 'product-description');
    desc.textContent = product.description || product.desc;
    info.appendChild(desc);
  }
  
  if (product.price || product.cost) {
    const price = el('p', 'product-price');
    price.textContent = product.price || product.cost;
    info.appendChild(price);
  }
  
  if (product.link || product.url) {
    const link = el('a', 'product-link');
    link.href = product.link || product.url;
    link.textContent = 'View Product';
    link.target = '_blank';
    info.appendChild(link);
  }
  
  card.appendChild(info);
  container.appendChild(card);
  return container;
}

function renderHTMLTable(htmlContent) {
  const container = el('div', 'structured-response');
  container.innerHTML = htmlContent;
  return container;
}

function renderPlainText(content) {
  const container = el('div', 'structured-response');
  container.textContent = content;
  return container;
}

// ---- Chat feed -------------------------------------------------------------
function clearFeed(){ $('#chat-box').innerHTML=''; }
function renderMessage(role, text, structuredContent = null){
  const g = el('div','msg-group '+(role==='user'?'user':''));
  const a = el('div','avatar'); a.textContent = role==='user'?'You':'AI';
  const bWrap = el('div','bubbles');
  
  // Add text content
  if (text) {
    const b = el('div','bubble'); b.textContent = text;
    bWrap.appendChild(b);
  }
  
  // Add structured content if present
  if (structuredContent) {
    const structuredEl = renderStructuredContent(structuredContent);
    bWrap.appendChild(structuredEl);
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
  send.disabled = input.value.trim().length===0;
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

  const chat = chats.find(c=>c.id===currentId);
  if (chat.messages.length===0) chat.title = text.slice(0,40);

  // Add user message to chat
  renderMessage('user', text);
  chat.messages.push({ role:'user', text });
  saveChats();

  input.value=''; input.dispatchEvent(new Event('input'));
  typing(true);

  try{
    const nlipMessage = {
      messagetype: "text",
      format: "text",
      subformat: "English",
      content: text
    };

    const res = await fetch('/nlip/', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify(nlipMessage)
    });
    const data = await res.json();
    typing(false);
    const response = (data && (data.content || data.message || data.reply)) || 'No response';
    
    // Try to detect if response contains structured data
    let structuredContent = null;
    let textContent = response;
    
    try {
      // Check if response is JSON
      const parsed = JSON.parse(response);
      if (Array.isArray(parsed) || typeof parsed === 'object') {
        structuredContent = response;
        textContent = null; // Don't show narrative text if we have structured data
      }
    } catch (e) {
      // Not JSON, check for HTML table structure or product-like content
      if (response.includes('<table>') || response.includes('|') || 
          response.includes('Product') || response.includes('Name') || 
          response.includes('Price') || response.includes('Description')) {
        structuredContent = response;
        textContent = null;
      }
    }
    
    renderMessage('assistant', textContent, structuredContent);
    chat.messages.push({ role:'assistant', text: textContent, structured: structuredContent });
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
