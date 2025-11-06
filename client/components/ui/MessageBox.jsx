export default function ChatBox({messages, isLoading}) {
  const renderMessageBubbles = () => {
    return (
      <div className="flex justify-start">
        <div className="bg-white text-gray-800 shadow-md rounded-2xl rounded-tl-sm border border-gray-200 px-4 py-3">
          <div className="flex space-x-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-gray-50 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-8">
          <p className="text-lg">Start a conversation!</p>
        </div>
      )}
      {messages.map((msg, index) => (
        <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
            msg.role === 'user' 
              ? 'bg-cyan-500 text-white rounded-tr-sm' 
              : 'bg-white text-gray-800 shadow-md rounded-tl-sm border border-gray-200'
          }`}>
            <p className="whitespace-pre-line wrap-break-words">{msg.content}</p>
          </div>
        </div>
      ))}
      {isLoading && (
        renderMessageBubbles()
      )}
    </div>
  )
}