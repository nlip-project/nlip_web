import { useState } from 'react';

import { NLIPClient } from '../../utils/nlip';

export default function InputForm({ setMessages, isLoading, setIsLoading }) {
  const [input, setInput] = useState('');
  const nlipClient = new NLIPClient();

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const data = await nlipClient.sendMessage(userMessage);
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