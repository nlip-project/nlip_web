import { useState } from 'react';

import { NLIPClient } from '../../utils/nlip';

export default function InputForm({ setMessages, isLoading, setIsLoading, allowFileUpload = false }) {
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const nlipClient = new NLIPClient();

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat with image data if present
    const messageData = {
      role: 'user',
      content: userMessage,
      image: selectedFile ? URL.createObjectURL(selectedFile) : null,
      fileName: selectedFile?.name
    };
    setMessages(prev => [...prev, messageData]);
    setIsLoading(true);

    try {
      let data;
      if (allowFileUpload && selectedFile) {
        data = await nlipClient.sendWithImage(userMessage, selectedFile);
        data = data.content;
        setSelectedFile(null);
      } else {
        data = await nlipClient.sendMessage(userMessage);
      }
      const botMessage = data || 'No response';
      
      // Add bot response to chat
      setMessages(prev => [...prev, { role: 'assistant', content: botMessage }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Error connecting to chat server.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <form onSubmit={sendMessage} className="border-t border-gray-200 bg-white p-4">
      <div className="flex gap-3">
        {allowFileUpload && (
          <>
            <input
              type="file"
              id="file-input"
              onChange={handleFileChange}
              className="hidden"
              accept="image/*"
              disabled={isLoading}
            />
            <label
              htmlFor="file-input"
              className={`px-4 py-3 border border-gray-300 rounded-xl cursor-pointer transition-colors ${
                selectedFile 
                  ? 'bg-cyan-100 border-cyan-500 text-cyan-700' 
                  : 'bg-white hover:bg-gray-50'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {selectedFile ? '📎 ' + selectedFile.name : '📎 Attach'}
            </label>
          </>
        )}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-semibold rounded-xl transition-colors duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </form>
  )
}