export default function ChecklistItem({ item, onToggle }) {
  const isDone = item.status === 'done'
  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0">
      <button
        data-testid={`toggle-${item.id}`}
        onClick={() => onToggle(item)}
        className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
          isDone ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'
        }`}
        aria-label={isDone ? 'Mark pending' : 'Mark done'}
      >
        {isDone && '✓'}
      </button>
      <span className={isDone ? 'line-through text-gray-400' : 'text-gray-800'}>
        {item.title}
      </span>
      <span className="ml-auto text-xs text-gray-400">{item.category}</span>
    </div>
  )
}
