export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
          isUser ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-900'
        }`}
      >
        <p>{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <p data-testid="sources" className="text-xs mt-1 opacity-70">
            Sources: {message.sources.join(', ')}
          </p>
        )}
      </div>
    </div>
  )
}
