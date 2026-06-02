import { useState, type FormEvent } from 'react'
import type { Event, EventCreate, EventUpdate } from '../types/event'

interface Props {
  mode: 'create' | 'edit'
  event?: Event
  defaultStart?: string  // "YYYY-MM-DD" from calendar date click
  onSubmit: (data: EventCreate | EventUpdate) => Promise<void>
  onClose: () => void
}

// "2026-06-10T09:00:00" → "2026-06-10T09:00"
function toDatetimeLocal(iso: string): string {
  return iso.slice(0, 16)
}

function parseError(err: unknown): string {
  if (axios_isAxiosError(err)) {
    const detail = (err as any).response?.data?.detail
    if (Array.isArray(detail)) return detail[0]?.msg ?? 'Validation error'
    if (typeof detail === 'string') return detail
  }
  return 'Something went wrong'
}

function axios_isAxiosError(err: unknown): boolean {
  return typeof err === 'object' && err !== null && 'response' in err
}

export default function EventFormModal({ mode, event, defaultStart, onSubmit, onClose }: Props) {
  const initStart = event
    ? toDatetimeLocal(event.start_datetime)
    : defaultStart ? `${defaultStart}T09:00` : ''

  const initEnd = event
    ? toDatetimeLocal(event.end_datetime)
    : defaultStart ? `${defaultStart}T10:00` : ''

  const [title, setTitle] = useState(event?.title ?? '')
  const [description, setDescription] = useState(event?.description ?? '')
  const [location, setLocation] = useState(event?.location ?? '')
  const [startDatetime, setStartDatetime] = useState(initStart)
  const [endDatetime, setEndDatetime] = useState(initEnd)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await onSubmit({
        title,
        description: description || undefined,
        location: location || undefined,
        start_datetime: startDatetime + ':00',
        end_datetime: endDatetime + ':00',
      })
    } catch (err) {
      setError(parseError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{mode === 'create' ? 'New Event' : 'Edit Event'}</h2>
          <button className="modal-close" onClick={onClose}>&#10005;</button>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description ?? ''}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              value={location ?? ''}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Start *</label>
              <input
                type="datetime-local"
                value={startDatetime}
                onChange={(e) => setStartDatetime(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>End *</label>
              <input
                type="datetime-local"
                value={endDatetime}
                onChange={(e) => setEndDatetime(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Saving…' : mode === 'create' ? 'Create Event' : 'Save Changes'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
