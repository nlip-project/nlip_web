# Testing Guide for NLIP Web Interface Pages

## Server Setup
Your server should be running at: `http://localhost:8010`

## Testing Checklist

### 1. **Page 1: Text Chat** (`/static/page1_text_chat.html`)
**URL**: `http://localhost:8010/static/page1_text_chat.html`

**What to test:**
- [ ] Page loads with your existing beautiful design
- [ ] Sidebar shows chat history (initially empty)
- [ ] "New chat" button works
- [ ] Settings modal opens and closes
- [ ] Theme switching works (light/dark/auto)
- [ ] Text input accepts messages
- [ ] Send button works
- [ ] Messages appear in chat bubbles with correct styling
- [ ] Chat history is saved and restored
- [ ] No file upload options (text-only interface)

**Test messages:**
- "Hello, how are you?"
- "What's the weather like?"
- "Help me with coding"

### 2. **Page 2: Structured Chat** (`/static/page2_structured_chat.html`)
**URL**: `http://localhost:8010/static/page2_structured_chat.html`

**What to test:**
- [ ] Page loads with same design as Page 1
- [ ] All basic functionality from Page 1 works
- [ ] Structured data responses are rendered properly
- [ ] Product tables display correctly
- [ ] Product cards show with images, titles, descriptions
- [ ] JSON data is parsed and displayed as HTML tables

**Test messages for structured data:**
- "Show me laptop computers"
- "Find smartphones under $500"
- "Create a product comparison table"
- "Search for books by Stephen King"

### 3. **Page 3: Text & Image Chat** (`/static/page3_text_image_chat.html`)
**URL**: `http://localhost:8010/static/page3_text_image_chat.html`

**What to test:**
- [ ] Page loads with same design as other pages
- [ ] Image upload button is visible (📷 Image)
- [ ] Can select and upload image files
- [ ] Image preview appears in attachment area
- [ ] Images show in chat bubbles
- [ ] Can send text with images
- [ ] Can remove attachments before sending
- [ ] Text responses work with image analysis

**Test scenarios:**
- Upload an image and ask "What's in this picture?"
- Upload multiple images
- Send text without images
- Try different image formats (JPG, PNG, GIF)

### 4. **Page 4: Multimedia Chat** (`/static/page4_multimedia_chat.html`)
**URL**: `http://localhost:8010/static/page4_multimedia_chat.html`

**What to test:**
- [ ] Page loads with same design as other pages
- [ ] Both image (📷) and audio (🎵) upload buttons visible
- [ ] Can upload images and audio files
- [ ] File previews show correct icons (🖼️ for images, 🎵 for audio)
- [ ] Multiple file types can be uploaded together
- [ ] Files display correctly in chat
- [ ] Can remove individual attachments
- [ ] Text responses work with multimedia analysis

**Test scenarios:**
- Upload an image and ask "Describe this image"
- Upload an audio file and ask "Transcribe this audio"
- Upload both image and audio together
- Try different audio formats (MP3, WAV, M4A)

## Design Consistency Checks

### Visual Design
- [ ] All pages have identical sidebar design
- [ ] Same top bar with NLIP logo and branding
- [ ] Consistent hero section styling
- [ ] Same message bubble design and colors
- [ ] Identical theme switching behavior
- [ ] Same settings modal design
- [ ] Consistent button styling and hover effects

### Functionality
- [ ] Chat history works across all pages (separate storage)
- [ ] Settings persist across page refreshes
- [ ] Theme switching works on all pages
- [ ] Send button enables/disables correctly
- [ ] Typing indicators work
- [ ] Error handling displays properly

## Common Issues to Watch For

### Potential Problems:
1. **JavaScript Errors**: Check browser console for errors
2. **File Upload Issues**: Ensure file types are accepted
3. **Styling Issues**: Check if CSS loads correctly
4. **NLIP Integration**: Verify API calls work with your backend
5. **Local Storage**: Check if chat history saves properly

### Browser Console Commands for Testing:
```javascript
// Check if NLIP client is loaded
console.log(window.NLIPClient);

// Check localStorage
console.log(localStorage.getItem('nlip_text_chat_history_v1'));
console.log(localStorage.getItem('nlip_structured_chat_history_v1'));
console.log(localStorage.getItem('nlip_text_image_chat_history_v1'));
console.log(localStorage.getItem('nlip_multimedia_chat_history_v1'));

// Check theme
console.log(document.documentElement.getAttribute('data-theme'));
```

## Expected Behavior

### All Pages Should:
- Load with your existing beautiful design
- Have working chat functionality
- Save chat history independently
- Support theme switching
- Show proper error messages if backend is unavailable
- Handle file uploads appropriately (where applicable)

### Page-Specific Behavior:
- **Page 1**: Text-only, no file uploads
- **Page 2**: Structured data rendering, product tables/cards
- **Page 3**: Image uploads with previews
- **Page 4**: Both image and audio uploads with previews

## Quick Test Script

1. **Open each page URL in browser**
2. **Test basic functionality** (send a message)
3. **Test theme switching** (light/dark)
4. **Test file uploads** (where applicable)
5. **Check browser console** for errors
6. **Verify design consistency** across all pages

## Troubleshooting

If something doesn't work:
1. Check browser console for JavaScript errors
2. Verify your uvicorn server is running
3. Check if `nlip.js` loads correctly
4. Ensure file paths are correct
5. Test with different browsers if needed

## Success Criteria

✅ **All pages load without errors**
✅ **Design is consistent across all pages**
✅ **File uploads work on Pages 3 & 4**
✅ **Structured data renders on Page 2**
✅ **Chat history saves and loads**
✅ **Theme switching works**
✅ **NLIP integration functions properly**
