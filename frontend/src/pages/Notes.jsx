import { useState } from 'react'
import { useNotes, useCreateNote, useDeleteNote } from '../hooks/useNotes'
import NoteCard from '../components/NoteCard'
import client from '../api/client'

export default function Notes() {
  const { data: notes = [], isLoading } = useNotes()
  const createNote = useCreateNote()
  const deleteNote = useDeleteNote()

  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const payload = { title, content, category: category || undefined }
    client.post('/notes', payload)
    createNote.mutate(payload, {
      onSuccess: () => {
        setTitle('')
        setContent('')
        setCategory('')
      },
    })
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Knowledge Base</h1>

      <form onSubmit={handleSubmit} aria-label="form" className="bg-white rounded-xl shadow p-4 mb-6 flex flex-col gap-3">
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <input
          placeholder="Category (optional)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <textarea
          placeholder="Content…"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={4}
          className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
        />
        <button
          type="submit"
          disabled={createNote.isPending}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
        >
          Add Note
        </button>
      </form>

      {isLoading ? (
        <p className="text-gray-400">Loading…</p>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {notes.map((note) => (
            <NoteCard key={note.id} note={note} onDelete={(id) => deleteNote.mutate(id)} />
          ))}
        </div>
      )}
    </div>
  )
}
