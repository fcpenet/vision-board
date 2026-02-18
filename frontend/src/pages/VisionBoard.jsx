import { Link } from 'react-router-dom'

const MILESTONES = [
  { emoji: '🇪🇸', label: 'Apply for DNV', done: false },
  { emoji: '✈️', label: 'Book flights to Alicante', done: false },
  { emoji: '🏠', label: 'Find apartment', done: false },
  { emoji: '📋', label: 'Complete checklist', done: false },
]

export default function VisionBoard() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Vision Board</h1>
      <p className="text-gray-500 mb-8">Kiko's Spain Digital Nomad Visa journey — Alicante 🌊</p>

      <div className="grid grid-cols-2 gap-4 mb-10">
        {MILESTONES.map((m) => (
          <div
            key={m.label}
            className="bg-gradient-to-br from-indigo-50 to-white rounded-2xl p-6 shadow flex items-center gap-3"
          >
            <span className="text-3xl">{m.emoji}</span>
            <span className={`font-medium ${m.done ? 'line-through text-gray-400' : 'text-gray-800'}`}>
              {m.label}
            </span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Link to="/checklist" className="block bg-indigo-600 text-white rounded-xl p-4 text-center hover:bg-indigo-700">
          <div className="text-2xl mb-1">✅</div>
          <div className="font-medium">Checklist</div>
        </Link>
        <Link to="/chat" className="block bg-emerald-600 text-white rounded-xl p-4 text-center hover:bg-emerald-700">
          <div className="text-2xl mb-1">💬</div>
          <div className="font-medium">Ask Mini-Me</div>
        </Link>
        <Link to="/notes" className="block bg-amber-500 text-white rounded-xl p-4 text-center hover:bg-amber-600">
          <div className="text-2xl mb-1">📝</div>
          <div className="font-medium">Notes</div>
        </Link>
      </div>
    </div>
  )
}
