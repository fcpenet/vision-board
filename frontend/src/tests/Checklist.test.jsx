import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Checklist from '../pages/Checklist'
import * as api from '../api/client'

vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  },
}))

const MOCK_ITEMS = [
  { id: 'item-1', title: 'Valid passport', category: 'documents', status: 'pending', description: null, due_date: null },
  { id: 'item-2', title: 'Health insurance', category: 'insurance', status: 'pending', description: null, due_date: null },
]

function wrapper({ children }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Checklist', () => {
  beforeEach(() => {
    api.default.get.mockResolvedValue({ data: MOCK_ITEMS })
    api.default.patch.mockResolvedValue({ data: { ...MOCK_ITEMS[0], status: 'done' } })
  })

  it('test_renders_checklist_with_items', async () => {
    render(<Checklist />, { wrapper })
    expect(await screen.findByText('Valid passport')).toBeInTheDocument()
    expect(await screen.findByText('Health insurance')).toBeInTheDocument()
  })

  it('test_checklist_item_toggle_calls_api', async () => {
    render(<Checklist />, { wrapper })
    const toggle = await screen.findByTestId('toggle-item-1')
    fireEvent.click(toggle)
    await waitFor(() => expect(api.default.patch).toHaveBeenCalledWith('/checklist/item-1', { status: 'done' }))
  })

  it('test_checklist_filters_by_category', async () => {
    render(<Checklist />, { wrapper })
    await screen.findByText('Valid passport')
    const filter = screen.getByTestId('filter-documents')
    fireEvent.click(filter)
    await waitFor(() => expect(api.default.get).toHaveBeenCalledWith('/checklist', { params: { category: 'documents' } }))
  })
})
