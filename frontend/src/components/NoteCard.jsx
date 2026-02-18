export default function NoteCard({ note, onDelete }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col gap-2">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{note.title}</h3>
          {note.category && (
            <span className="text-xs text-indigo-600 font-medium">{note.category}</span>
          )}
        </div>
        <button
          onClick={() => onDelete(note.id)}
          className="text-gray-400 hover:text-red-500 text-sm"
          aria-label="Delete note"
        >
          ✕
        </button>
      </div>
      <p className="text-xs text-gray-400">{new Date(note.created_at).toLocaleDateString()}</p>
    </div>
  )
}
