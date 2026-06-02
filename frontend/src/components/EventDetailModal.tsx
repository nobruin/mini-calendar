import { useState } from 'react'
import type { Event } from '../types/event'

interface Props {
  event: Event
  onEdit: () => void
  onDelete: () => Promise<void>
  onCancel: () => Promise<void>
  onClose: () => void
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function EventDetailModal({ event, onEdit, onDelete, onCancel, onClose }: Props) {
  const [loading, setLoading] = useState(false)

  const run = async (action: () => Promise<void>) => {
    setLoading(true)
    try {
      await action()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{event.title}</h2>
          <button className="modal-close" onClick={onClose}>&#10005;</button>
        </div>

        <span className={`status-badge status-${event.status}`}>
          {event.status}
        </span>

        <div className="detail-field">
          <div className="detail-label">When</div>
          <div>{formatDate(event.start_datetime)}</div>
          <div className="detail-sub">to {formatDate(event.end_datetime)}</div>
        </div>

        {event.location && (
          <div className="detail-field">
            <div className="detail-label">Location</div>
            <div>{event.location}</div>
          </div>
        )}

        {event.description && (
          <div className="detail-field">
            <div className="detail-label">Description</div>
            <div>{event.description}</div>
          </div>
        )}

        <div className="modal-actions">
          {event.status === 'scheduled' && (
            <>
              <button className="btn btn-primary" onClick={onEdit} disabled={loading}>
                Edit
              </button>
              <button
                className="btn btn-secondary"
                disabled={loading}
                onClick={() => run(onCancel)}
              >
                Cancel Event
              </button>
            </>
          )}
          <button
            className="btn btn-danger"
            disabled={loading}
            onClick={() => {
              if (window.confirm('Delete this event permanently?')) {
                run(onDelete)
              }
            }}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
