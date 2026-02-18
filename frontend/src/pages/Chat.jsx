import { useState } from 'react'
import { useChat } from '../hooks/useChat'
import ChatWindow from '../components/ChatWindow'

export default function Chat() {
  const { messages, loading, sendMessage } = useChat()
  const [input, setInput] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const q = input.trim()
    if (!q) return
    setInput('')
    sendMessage(q)
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-gray-900">Ask Mini-Me</h1>
        <p className="text-sm text-gray-500">Ask anything about your Spain journey.</p>
      </div>

      <ChatWindow messages={messages} />

      <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your Spain journey…"
          className="flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-indigo-600 text-white px-4 py-2 rounded-xl text-sm disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}
