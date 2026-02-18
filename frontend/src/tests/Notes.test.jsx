import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Notes from '../pages/Notes'
import * as api from '../api/client'

vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

const MOCK_NOTES = [
  { id: 'note-1', title: 'Why Alicante', category: 'decisions', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
]

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Notes', () => {
  beforeEach(() => {
    api.default.get.mockResolvedValue({ data: MOCK_NOTES })
    api.default.post.mockResolvedValue({
      data: { id: 'note-2', title: 'New Note', category: 'general', created_at: '2024-01-02T00:00:00Z', updated_at: '2024-01-02T00:00:00Z' },
    })
  })

  it('test_note_form_submit_adds_note_to_list', async () => {
    render(<Notes />, { wrapper })
    await screen.findByText('Why Alicante')

    fireEvent.change(screen.getByPlaceholderText(/title/i), { target: { value: 'New Note' } })
    fireEvent.change(screen.getByPlaceholderText(/content/i), { target: { value: 'Some content' } })
    fireEvent.submit(screen.getByRole('form'))

    await waitFor(() =>
      expect(api.default.post).toHaveBeenCalledWith('/notes', expect.objectContaining({ title: 'New Note' }))
    )
  })
})
