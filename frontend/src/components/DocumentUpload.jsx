import { useState } from 'react'
import client from '../api/client'

export default function DocumentUpload({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState(null) // 'success' | 'error' | null
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  function handleFileChange(e) {
    setFile(e.target.files[0] ?? null)
    setStatus(null)
    setMessage('')
  }

  async function handleUpload() {
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setStatus('error')
      setMessage('Only PDF files are accepted.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    setLoading(true)
    try {
      const { data } = await client.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setStatus('success')
      setMessage(`${data.filename} uploaded successfully (${data.chunk_count} chunks).`)
      onUploaded?.(data)
    } catch {
      setStatus('error')
      setMessage('Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col gap-3">
      <h3 className="font-semibold text-gray-800">Upload Document</h3>
      <input
        data-testid="file-input"
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="text-sm"
      />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
      >
        {loading ? 'Uploading…' : 'Upload'}
      </button>
      {status === 'success' && <p className="text-green-600 text-sm">{message}</p>}
      {status === 'error' && <p className="text-red-500 text-sm">{message}</p>}
    </div>
  )
}
