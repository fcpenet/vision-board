import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import VisionBoard from '../pages/VisionBoard'

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('VisionBoard', () => {
  it('test_renders_vision_board_page', () => {
    render(<VisionBoard />, { wrapper })
    expect(screen.getByText(/vision board/i)).toBeInTheDocument()
  })
})
