# nlip_web

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)

A NLIP web server with a JavaScript client for displaying products and handling multimodal chat interactions.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Text Chat | ![Complete](https://img.shields.io/badge/status-complete-success) | Simple text-only conversations |
| Structured Chat | ![Complete](https://img.shields.io/badge/status-complete-success) | Product display with JSON parsing |
| Image Chat | ![Complete](https://img.shields.io/badge/status-complete-success) | Text + image upload and analysis |
| Multimedia Chat | ![Complete](https://img.shields.io/badge/status-complete-success) | Text + image + audio support |
| Product Display | ![Complete](https://img.shields.io/badge/status-complete-success) | Beautiful product tables and cards |
| React Components | ![In Progress](https://img.shields.io/badge/status-in_progress-yellow) | Reusable React components |
| Documentation | ![Complete](https://img.shields.io/badge/status-complete-success) | Comprehensive development guide |

## Quick Start

### Prerequisites
- Python 3.10+
- Poetry (Python package manager)
- Ollama running locally (for AI chat)

### Installation

```bash
# Clone the repository
git clone https://github.com/nlip-project/nlip_web.git
cd nlip_web

# Install dependencies
poetry install
```

### Running the Server

**Text Chat Server (Pages 1 & 2)**
```bash
poetry run python scripts.py chat --port 8010
```

**Image Chat Server (Pages 3 & 4)**
```bash
poetry run python scripts.py image --port 8020
```

### Access the Application

- **Page 1 (Text Chat)**: `http://localhost:8010/static/page1_text_chat.html`
- **Page 2 (Structured Chat)**: `http://localhost:8010/static/page2_structured_chat.html`
- **Page 3 (Image Chat)**: `http://localhost:8020/static/page3_text_image_chat.html`
- **Page 4 (Multimedia Chat)**: `http://localhost:8020/static/page4_multimedia_chat.html`

## Documentation

| Document | Status | Description |
|----------|--------|-------------|
| [Development Guide](ETHAN_DEVELOPMENT_GUIDE.md) | ![Accepted](https://img.shields.io/badge/status-accepted-success) | Comprehensive guide for developers |

## Core Functionality

The primary goal is to **display products nicely** on screen. The system receives JSON product data, parses it, and renders beautiful product tables and cards.

## Contributing

We welcome contributions! Please see our [Development Guide](ETHAN_DEVELOPMENT_GUIDE.md) for details.

## License

Apache-2.0 License - see [LICENSE](LICENSE) file for details.
