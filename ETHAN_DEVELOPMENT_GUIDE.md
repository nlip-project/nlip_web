# NLIP Web Development Guide for Ethan

![Status](https://img.shields.io/badge/status-accepted-success)
![Last Updated](https://img.shields.io/badge/last_updated-2025--01--22-blue)

## Quick Start

Hey Ethan! This guide will help you understand the NLIP web project, how to run it, test it, and contribute to the codebase.

## Documentation Status

This documentation uses status badges to track completion and review status:

| Section | Status | Notes |
|---------|--------|-------|
| Quick Start | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Setup & Installation | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Running the Server | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Available Pages & Features | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Testing Guide | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Code Architecture | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Adding New Features | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Common Issues & Solutions | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |
| Development Workflow | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Complete |

**Status Legend:**
- ![Accepted](https://img.shields.io/badge/status-accepted-success) **Accepted** - Complete and approved
- ![In Progress](https://img.shields.io/badge/status-in_progress-yellow) **In Progress** - Currently being written/updated
- ![Needs Review](https://img.shields.io/badge/status-needs_review-orange) **Needs Review** - Requires review/feedback
- ![Planned](https://img.shields.io/badge/status-planned-blue) **Planned** - Planned for future

## Table of Contents
1. [Project Overview](#project-overview)
2. [Setup & Installation](#setup--installation)
3. [Running the Server](#running-the-server)
4. [Available Pages & Features](#available-pages--features)
5. [Testing Guide](#testing-guide)
6. [Code Architecture](#code-architecture)
7. [Adding New Features](#adding-new-features)
8. [Common Issues & Solutions](#common-issues--solutions)
9. [Development Workflow](#development-workflow)

---

## Project Overview

**NLIP Web** is a modern chat interface with 4 different page types, each designed for specific use cases:

- **Text Chat**: Simple text-only conversations
- **Structured Chat**: Text input with structured data responses (tables, products)
- **Image Chat**: Text + image upload and analysis
- **Multimedia Chat**: Text + image + audio upload and analysis

All pages share a beautiful, consistent design with purple theming, dark/light mode, and professional typography.

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Poetry (Python package manager)
- Git

### Installation Steps

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd nlip_web
   ```

2. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

3. **Verify installation**:
   ```bash
   poetry run python --version
   ```

### Project Structure
```
nlip_web/
Ôö£ÔöÇÔöÇ nlip_web/           # Python backend modules
Ôöé   Ôö£ÔöÇÔöÇ run_echo.py     # Main server entry point
Ôöé   Ôö£ÔöÇÔöÇ text_chat.py    # Text chat backend
Ôöé   Ôö£ÔöÇÔöÇ image_chat.py   # Image chat backend
Ôöé   ÔööÔöÇÔöÇ ...
Ôö£ÔöÇÔöÇ static/             # Frontend files
Ôöé   Ôö£ÔöÇÔöÇ styles.css      # Main stylesheet (beautiful design!)
Ôöé   Ôö£ÔöÇÔöÇ nlip.js         # NLIP client library
Ôöé   Ôö£ÔöÇÔöÇ page1_text_chat.html      # Text-only chat
Ôöé   Ôö£ÔöÇÔöÇ page2_structured_chat.html # Structured data chat
Ôöé   Ôö£ÔöÇÔöÇ page3_text_image_chat.html # Image chat
Ôöé   Ôö£ÔöÇÔöÇ page4_multimedia_chat.html # Multimedia chat
Ôöé   ÔööÔöÇÔöÇ ...
Ôö£ÔöÇÔöÇ scripts.py          # Helper scripts
ÔööÔöÇÔöÇ pyproject.toml      # Poetry configuration
```

---

## Running the Server

### Option 1: Main Server (Recommended)
```bash
poetry run uvicorn nlip_web.run_echo:build --factory --reload --port 8010
```

### Option 2: Using Helper Scripts
```bash
# Text chat server
poetry run python scripts.py chat --port 8010

# Image chat server  
poetry run python scripts.py image --port 8020
```

### Access the Application
Once running, open your browser to:
- **Main interface**: `http://localhost:8010`
- **Page 1 (Text Chat)**: `http://localhost:8010/static/page1_text_chat.html`
- **Page 2 (Structured)**: `http://localhost:8010/static/page2_structured_chat.html`
- **Page 3 (Image)**: `http://localhost:8010/static/page3_text_image_chat.html`
- **Page 4 (Multimedia)**: `http://localhost:8010/static/page4_multimedia_chat.html`

---

## Available Pages & Features

### Page 1: Text Chat (`page1_text_chat.html`)
**Purpose**: Simple text-only conversations
- Text input and responses
- Chat history
- Theme switching (light/dark/auto)
- Settings modal
- No file uploads

**Test with**: "Hello, how are you?", "Help me with coding"

### Page 2: Structured Chat (`page2_structured_chat.html`)
**Purpose**: Text input with structured data responses
- All Page 1 features
- Product tables and cards
- JSON parsing and HTML rendering
- Structured data display

**Test with**: "Show me laptop computers", "Create a product comparison table"

### Page 3: Image Chat (`page3_text_image_chat.html`)
**Purpose**: Text + image upload and analysis
- All Page 1 features
- Image upload button
- Image previews in chat
- Image analysis responses

**Test with**: Upload an image and ask "What's in this picture?"

### Page 4: Multimedia Chat (`page4_multimedia_chat.html`)
**Purpose**: Text + image + audio upload and analysis
- All Page 1 features
- Image upload button
- Audio upload button
- Multiple file type support
- File previews and removal

**Test with**: Upload both image and audio files together

---

## Testing Guide

### Quick Testing Checklist

1. **Start the server**:
   ```bash
   poetry run uvicorn nlip_web.run_echo:build --factory --reload --port 8010
   ```

2. **Test each page**:
   - Open each URL in your browser
   - Send a test message
   - Try theme switching
   - Test file uploads (Pages 3 & 4)
   - Check browser console for errors

3. **Verify design consistency**:
   - All pages should look identical
   - Same sidebar, top bar, and chat interface
   - Consistent purple theming
   - Professional typography (Inter font)

### Browser Console Testing
- Check NLIP client: `console.log(window.NLIPClient)`
- Check chat history: `console.log(localStorage.getItem('nlip_text_chat_history_v1'))`
- Check theme: `console.log(document.documentElement.getAttribute('data-theme'))`

### Common Test Scenarios

**Text Chat (Page 1)**:
- Send: "Hello, how are you?"
- Send: "What's the weather like?"
- Send: "Help me with coding"

**Structured Chat (Page 2)**:
- Send: "Show me laptop computers"
- Send: "Find smartphones under $500"
- Send: "Create a product comparison table"

**Image Chat (Page 3)**:
- Upload an image and ask: "What's in this picture?"
- Upload multiple images
- Try different formats (JPG, PNG, GIF)

**Multimedia Chat (Page 4)**:
- Upload an image and ask: "Describe this image"
- Upload an audio file and ask: "Transcribe this audio"
- Upload both image and audio together

---

## Code Architecture

### Frontend Structure

**Main Files**:
- `static/styles.css` - Beautiful CSS with purple theming and Inter font
- `static/nlip.js` - NLIP client library for API communication
- `static/common.css` - Shared styles across all pages
- `static/common.js` - Shared JavaScript utilities

**Page-Specific Files**:
- `page1_text_chat.html` + `page1_working.js` - Text-only chat
- `page2_structured_chat.html` + `page2_structured_script.js` - Structured data
- `page3_text_image_chat.html` + `page3_text_image_script.js` - Image chat
- `page4_multimedia_chat.html` + `page4_multimedia_script.js` - Multimedia

### Backend Structure

**Main Server**: `nlip_web/run_echo.py`
- FastAPI-based web server
- Serves static files
- Handles API endpoints

**Chat Modules**:
- `text_chat.py` - Text-only chat backend
- `image_chat.py` - Image chat backend
- `genai.py` - AI/ML integration
- `nlip_ext.py` - NLIP extensions

### Key Technologies
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python, FastAPI, Uvicorn
- **Styling**: Custom CSS with CSS variables, modern typography
- **Storage**: LocalStorage for chat history and settings

---

## Adding New Features

### Adding a New Page Type

1. **Create HTML file** in `static/` (copy from existing page and modify)
2. **Create JavaScript file** in `static/` (copy from existing script and modify functionality)
3. **Update localStorage keys** to be unique for the new page
4. **Test the new page** at `http://localhost:8010/static/your_new_page.html`

### Modifying Existing Features

- **Styling**: Edit `static/styles.css` for global changes
- **Functionality**: Edit the appropriate JavaScript file and update HTML if needed
- **Backend**: Edit files in `nlip_web/` directory and restart server

### Best Practices

- Maintain design consistency using existing CSS classes
- Keep localStorage keys unique per page
- Test changes across all pages
- Use descriptive names for files and functions

---

## Common Issues & Solutions

### Common Issues

**Server Won't Start**: Check if port is in use, try different port (8011, 8012, etc.)

**Pages Won't Load**: Verify server is running, check URL, check browser console

**File Uploads Not Working**: Check file size limits, verify file types, check console errors

**Styling Issues**: Hard refresh browser (Ctrl+F5), check CSS loading, verify no JS errors

**Chat History Not Saving**: Check localStorage in console, verify unique storage keys

---

## Development Workflow

### Daily Development Process

1. Start development server: `poetry run uvicorn nlip_web.run_echo:build --factory --reload --port 8010`
2. Make changes to HTML, CSS, or JavaScript files
3. Test changes in browser (auto-reload should work)
4. Check browser console for errors
5. Test across all pages to ensure consistency

### Git Workflow

1. Before starting work: `git pull origin main`
2. Make your changes and test thoroughly
3. Commit changes: `git add . && git commit -m "Description" && git push origin main`

### Code Review Checklist

- All pages still load correctly
- No JavaScript errors in console
- Design remains consistent
- New features work as expected
- No breaking changes to existing functionality

---

## Getting Help

### Resources
- Existing guides: `static/TESTING_GUIDE.md`, `static/PAGE_TYPES_SUMMARY.md`
- Code comments: Check existing code for examples
- Browser developer tools: Use F12 to debug issues

### Common Commands
- Start server: `poetry run uvicorn nlip_web.run_echo:build --factory --reload --port 8010`
- Install dependencies: `poetry install`
- Check Python version: `poetry run python --version`
- Run specific chat server: `poetry run python scripts.py chat --port 8010`
- Check what's running on port: `netstat -an | grep 8010`

---

## Success Criteria

You'll know everything is working when:
- Server starts without errors
- All 4 pages load correctly
- Chat functionality works on all pages
- File uploads work on Pages 3 & 4
- Theme switching works
- Design is consistent across all pages
- No JavaScript errors in console

---

**Happy coding, Ethan!**

This guide should get you up and running quickly. If you run into any issues or need clarification on anything, don't hesitate to ask!
