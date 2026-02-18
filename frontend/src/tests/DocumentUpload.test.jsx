import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import DocumentUpload from '../components/DocumentUpload'
import * as api from '../api/client'

vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

describe('DocumentUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('test_document_upload_shows_success_state', async () => {
    api.default.post.mockResolvedValue({ data: { id: 'doc-1', filename: 'guide.pdf', chunk_count: 3 } })
    render(<DocumentUpload />)

    const file = new File(['pdf content'], 'guide.pdf', { type: 'application/pdf' })
    const input = screen.getByTestId('file-input')
    fireEvent.change(input, { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    expect(await screen.findByText(/uploaded successfully/i)).toBeInTheDocument()
  })

  it('test_document_upload_shows_error_on_non_pdf', async () => {
    render(<DocumentUpload />)

    const file = new File(['plain text'], 'notes.txt', { type: 'text/plain' })
    const input = screen.getByTestId('file-input')
    fireEvent.change(input, { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    expect(await screen.findByText(/only pdf/i)).toBeInTheDocument()
  })
})
