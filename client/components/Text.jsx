import { useState } from 'react';
import MessageBox from './ui/MessageBox';
import InputForm from './ui/InputForm';

import ChatContainer from './ui/ChatContainer';

export default function Text() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
      <ChatContainer header="NLIP Client">
        <MessageBox messages={messages} isLoading={isLoading} />
        <InputForm setMessages={setMessages} isLoading={isLoading} setIsLoading={setIsLoading} />
      </ChatContainer>
    </div>
  );
}
