import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Chat from '../pages/Chat'
import * as api from '../api/client'

vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Chat', () => {
  beforeEach(() => {
    api.default.post.mockResolvedValue({
      data: { answer: 'Alicante has 320 sunny days.', sources: ['note-1'] },
    })
  })

  it('test_chat_input_submits_query', async () => {
    render(<Chat />, { wrapper })
    const input = screen.getByPlaceholderText(/ask/i)
    fireEvent.change(input, { target: { value: 'Why Alicante?' } })
    fireEvent.submit(input.closest('form'))
    await waitFor(() => expect(api.default.post).toHaveBeenCalledWith('/chat', { query: 'Why Alicante?' }))
  })

  it('test_chat_displays_assistant_response', async () => {
    render(<Chat />, { wrapper })
    const input = screen.getByPlaceholderText(/ask/i)
    fireEvent.change(input, { target: { value: 'Why Alicante?' } })
    fireEvent.submit(input.closest('form'))
    expect(await screen.findByText('Alicante has 320 sunny days.')).toBeInTheDocument()
  })

  it('test_chat_displays_source_references', async () => {
    render(<Chat />, { wrapper })
    const input = screen.getByPlaceholderText(/ask/i)
    fireEvent.change(input, { target: { value: 'Why Alicante?' } })
    fireEvent.submit(input.closest('form'))
    expect(await screen.findByTestId('sources')).toBeInTheDocument()
  })
})
