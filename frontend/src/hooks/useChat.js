import { useState } from 'react'
import client from '../api/client'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  async function sendMessage(query) {
    setMessages((prev) => [...prev, { role: 'user', content: query }])
    setLoading(true)
    try {
      const { data } = await client.post('/chat', { query })
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } finally {
      setLoading(false)
    }
  }

  return { messages, loading, sendMessage }
}
