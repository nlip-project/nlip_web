/**
 * NLIP Common JavaScript Library
 * This file contains common utilities and functions that can be shared across all NLIP page types
 */

import { NLIPClient, NLIPFactory, AllowedFormats } from './nlip.js';

/**
 * Common NLIP Client with enhanced functionality
 */
class CommonNLIPClient extends NLIPClient {
  constructor(baseUrl = '', options = {}) {
    super(baseUrl, options);
    this.conversationHistory = [];
    this.isLoading = false;
  }

  /**
   * Send text message and handle response
   */
  async sendTextMessage(text) {
    if (this.isLoading) return null;
    
    this.isLoading = true;
    try {
      const response = await this.sendMessage(text);
      this.conversationHistory.push({ type: 'user', content: text });
      this.conversationHistory.push({ type: 'bot', content: response });
      return response;
    } catch (error) {
      console.error('Error sending text message:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Send message with image attachment
   */
  async sendMessageWithImage(text, imageFile) {
    if (this.isLoading) return null;
    
    this.isLoading = true;
    try {
      const base64 = await this.fileToBase64(imageFile);
      const message = NLIPFactory.createText(text);
      message.addImage(base64, this.getFileExtension(imageFile));
      
      if (this.correlator != null) {
        message.addConversationToken(this.correlator);
      }
      
      const response = await this.send(message);
      const nlipMessage = NLIPFactory.createMessageFromJSON(response);
      this.correlator = nlipMessage.extractToken('conversation');
      
      const extractedText = nlipMessage.extractText();
      this.conversationHistory.push({ type: 'user', content: text, files: [imageFile.name] });
      this.conversationHistory.push({ type: 'bot', content: extractedText });
      
      return extractedText;
    } catch (error) {
      console.error('Error sending message with image:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Send message with multiple file attachments (text, images, audio)
   */
  async sendMessageWithFiles(text, files) {
    if (this.isLoading) return null;
    
    this.isLoading = true;
    try {
      const message = NLIPFactory.createText(text);
      const fileNames = [];
      
      for (const file of files) {
        const base64 = await this.fileToBase64(file);
        const extension = this.getFileExtension(file);
        
        if (this.isImageFile(file)) {
          message.addImage(base64, extension);
        } else if (this.isAudioFile(file)) {
          message.addAudio(base64, extension);
        } else {
          // Handle other file types as binary
          message.addBinary(base64, 'file', extension);
        }
        
        fileNames.push(file.name);
      }
      
      if (this.correlator != null) {
        message.addConversationToken(this.correlator);
      }
      
      const response = await this.send(message);
      const nlipMessage = NLIPFactory.createMessageFromJSON(response);
      this.correlator = nlipMessage.extractToken('conversation');
      
      const extractedText = nlipMessage.extractText();
      this.conversationHistory.push({ type: 'user', content: text, files: fileNames });
      this.conversationHistory.push({ type: 'bot', content: extractedText });
      
      return extractedText;
    } catch (error) {
      console.error('Error sending message with files:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Check if file is an image
   */
  isImageFile(file) {
    return file.type.startsWith('image/');
  }

  /**
   * Check if file is an audio file
   */
  isAudioFile(file) {
    return file.type.startsWith('audio/');
  }

  /**
   * Get conversation history
   */
  getConversationHistory() {
    return this.conversationHistory;
  }

  /**
   * Clear conversation history
   */
  clearConversationHistory() {
    this.conversationHistory = [];
    this.correlator = null;
  }
}

/**
 * UI Helper Functions
 */
class NLIPUIHelper {
  /**
   * Create a message element
   */
  static createMessageElement(type, content, files = []) {
    const messageGroup = document.createElement('div');
    messageGroup.className = `message-group ${type}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = type === 'user' ? 'U' : 'B';
    messageGroup.appendChild(avatar);
    
    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (files.length > 0) {
      const fileList = document.createElement('div');
      fileList.style.fontSize = '12px';
      fileList.style.opacity = '0.8';
      fileList.style.marginBottom = '8px';
      fileList.innerHTML = `📎 ${files.join(', ')}`;
      bubble.appendChild(fileList);
    }
    
    bubble.appendChild(document.createTextNode(content));
    messageGroup.appendChild(bubble);
    
    return messageGroup;
  }

  /**
   * Add message to chat container
   */
  static addMessageToChat(chatContainer, type, content, files = []) {
    const messageElement = this.createMessageElement(type, content, files);
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageElement;
  }

  /**
   * Show loading state
   */
  static showLoading(container) {
    const loadingElement = document.createElement('div');
    loadingElement.className = 'message-group';
    loadingElement.innerHTML = `
      <div class="avatar">B</div>
      <div class="message-bubble">
        <div class="loading">
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
          <div class="loading-dot"></div>
        </div>
      </div>
    `;
    container.appendChild(loadingElement);
    container.scrollTop = container.scrollHeight;
    return loadingElement;
  }

  /**
   * Remove loading state
   */
  static removeLoading(loadingElement) {
    if (loadingElement && loadingElement.parentNode) {
      loadingElement.parentNode.removeChild(loadingElement);
    }
  }

  /**
   * Show error message
   */
  static showError(container, message) {
    const errorElement = document.createElement('div');
    errorElement.className = 'status-message status-error';
    errorElement.innerHTML = `❌ ${message}`;
    container.appendChild(errorElement);
    
    // Remove error after 5 seconds
    setTimeout(() => {
      if (errorElement.parentNode) {
        errorElement.parentNode.removeChild(errorElement);
      }
    }, 5000);
  }

  /**
   * Create file list display
   */
  static createFileList(files) {
    const fileList = document.createElement('ul');
    fileList.className = 'file-list';
    
    Array.from(files).forEach(file => {
      const fileItem = document.createElement('li');
      fileItem.className = 'file-item';
      
      const icon = this.getFileIcon(file);
      const size = this.formatFileSize(file.size);
      
      fileItem.innerHTML = `
        <span class="file-icon">${icon}</span>
        <span class="file-name">${file.name}</span>
        <span class="file-size">${size}</span>
        <button class="remove-file" onclick="this.parentElement.remove()">×</button>
      `;
      
      fileList.appendChild(fileItem);
    });
    
    return fileList;
  }

  /**
   * Get file icon based on file type
   */
  static getFileIcon(file) {
    if (file.type.startsWith('image/')) return '🖼️';
    if (file.type.startsWith('audio/')) return '🎵';
    if (file.type.startsWith('video/')) return '🎬';
    if (file.type.includes('pdf')) return '📄';
    if (file.type.includes('text')) return '📝';
    return '📎';
  }

  /**
   * Format file size
   */
  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Render structured content (for Page 2)
   */
  static renderStructuredContent(content) {
    try {
      // Try to parse as JSON first
      const data = JSON.parse(content);
      
      if (Array.isArray(data) && data.length > 0) {
        // Render as product table
        return this.renderProductTable(data);
      } else if (typeof data === 'object') {
        // Render as product card
        return this.renderProductCard(data);
      }
    } catch (e) {
      // If not JSON, try to detect HTML-like structure
      if (content.includes('<table>') || content.includes('<tr>')) {
        return this.renderHTMLTable(content);
      }
    }
    
    // Fallback: render as plain text
    return this.renderPlainText(content);
  }

  /**
   * Render product table
   */
  static renderProductTable(products) {
    const table = document.createElement('table');
    table.className = 'product-table';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const headers = Object.keys(products[0]);
    headers.forEach(header => {
      const th = document.createElement('th');
      th.textContent = header.charAt(0).toUpperCase() + header.slice(1);
      headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    products.forEach(product => {
      const row = document.createElement('tr');
      headers.forEach(header => {
        const td = document.createElement('td');
        td.textContent = product[header] || '';
        row.appendChild(td);
      });
      tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    return table;
  }

  /**
   * Render product card
   */
  static renderProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    if (product.image) {
      const img = document.createElement('img');
      img.className = 'product-image';
      img.src = product.image;
      img.alt = product.name || 'Product';
      card.appendChild(img);
    }
    
    const info = document.createElement('div');
    info.className = 'product-info';
    
    if (product.name) {
      const title = document.createElement('h3');
      title.className = 'product-title';
      title.textContent = product.name;
      info.appendChild(title);
    }
    
    if (product.description) {
      const desc = document.createElement('p');
      desc.className = 'product-description';
      desc.textContent = product.description;
      info.appendChild(desc);
    }
    
    if (product.price) {
      const price = document.createElement('p');
      price.className = 'product-price';
      price.textContent = product.price;
      info.appendChild(price);
    }
    
    card.appendChild(info);
    return card;
  }

  /**
   * Render HTML table
   */
  static renderHTMLTable(htmlContent) {
    const container = document.createElement('div');
    container.className = 'structured-content';
    container.innerHTML = htmlContent;
    return container;
  }

  /**
   * Render plain text
   */
  static renderPlainText(content) {
    const container = document.createElement('div');
    container.className = 'structured-content';
    container.textContent = content;
    return container;
  }
}

/**
 * Common form handling utilities
 */
class NLIPFormHelper {
  /**
   * Setup common form event listeners
   */
  static setupForm(formId, chatBoxId, client) {
    const form = document.getElementById(formId);
    const chatBox = document.getElementById(chatBoxId);
    
    if (!form || !chatBox) {
      console.error('Form or chat box element not found');
      return;
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const input = form.querySelector('input[type="text"], textarea');
      const fileInput = form.querySelector('input[type="file"]');
      
      if (!input) {
        console.error('Text input not found');
        return;
      }

      const message = input.value.trim();
      if (!message) return;

      // Add user message to chat
      NLIPUIHelper.addMessageToChat(chatBox, 'user', message);
      
      // Clear input
      input.value = '';
      
      // Show loading
      const loadingElement = NLIPUIHelper.showLoading(chatBox);
      
      try {
        let response;
        
        if (fileInput && fileInput.files.length > 0) {
          // Handle file uploads
          const files = Array.from(fileInput.files);
          response = await client.sendMessageWithFiles(message, files);
          
          // Clear file input
          fileInput.value = '';
          if (fileInput.nextElementSibling && fileInput.nextElementSibling.classList.contains('file-list')) {
            fileInput.nextElementSibling.remove();
          }
        } else {
          // Handle text only
          response = await client.sendTextMessage(message);
        }
        
        // Remove loading and add response
        NLIPUIHelper.removeLoading(loadingElement);
        NLIPUIHelper.addMessageToChat(chatBox, 'bot', response);
        
      } catch (error) {
        NLIPUIHelper.removeLoading(loadingElement);
        NLIPUIHelper.showError(chatBox, 'Error: ' + error.message);
        console.error('Form submission error:', error);
      }
    });
  }

  /**
   * Setup file input handling
   */
  static setupFileInput(fileInputId, displayContainerId) {
    const fileInput = document.getElementById(fileInputId);
    const displayContainer = document.getElementById(displayContainerId);
    
    if (!fileInput) return;

    fileInput.addEventListener('change', () => {
      if (displayContainer) {
        displayContainer.innerHTML = '';
        if (fileInput.files.length > 0) {
          const fileList = NLIPUIHelper.createFileList(fileInput.files);
          displayContainer.appendChild(fileList);
        }
      }
    });
  }
}

// Export classes for use in other files
export { CommonNLIPClient, NLIPUIHelper, NLIPFormHelper };
