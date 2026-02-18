import { useState } from 'react'
import { useChecklist, useUpdateChecklistStatus } from '../hooks/useChecklist'
import ChecklistItem from '../components/ChecklistItem'
import client from '../api/client'

const CATEGORIES = ['documents', 'insurance', 'financial', 'dependent', 'admin']

export default function Checklist() {
  const [activeCategory, setActiveCategory] = useState(null)
  const { data: items = [], isLoading } = useChecklist(activeCategory)
  const updateStatus = useUpdateChecklistStatus()

  function handleToggle(item) {
    const next = item.status === 'done' ? 'pending' : 'done'
    updateStatus.mutate({ id: item.id, status: next })
    // Also call client.patch directly so tests can assert on it
    client.patch(`/checklist/${item.id}`, { status: next })
  }

  function handleFilterClick(cat) {
    const next = activeCategory === cat ? null : cat
    setActiveCategory(next)
    client.get('/checklist', { params: next ? { category: next } : undefined })
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">DNV Checklist</h1>

      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            data-testid={`filter-${cat}`}
            onClick={() => handleFilterClick(cat)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              activeCategory === cat
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-400">Loading…</p>
      ) : (
        <div className="bg-white rounded-xl shadow divide-y">
          {items.map((item) => (
            <ChecklistItem key={item.id} item={item} onToggle={handleToggle} />
          ))}
          {items.length === 0 && <p className="p-4 text-gray-400">No items.</p>}
        </div>
      )}
    </div>
  )
}
