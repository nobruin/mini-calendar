import { useState, useEffect, useCallback } from 'react'
import { useTheme } from './hooks/useTheme'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin, { type DateClickArg } from '@fullcalendar/interaction'
import type { EventClickArg } from '@fullcalendar/core'
import * as api from './api/events'
import type { Event, EventCreate, EventUpdate } from './types/event'
import EventFormModal from './components/EventFormModal'
import EventDetailModal from './components/EventDetailModal'
import './index.css'

type FormModalState =
  | { mode: 'create'; defaultStart: string }
  | { mode: 'edit'; event: Event }

export default function App() {
  const { theme, toggle } = useTheme()
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formModal, setFormModal] = useState<FormModalState | null>(null)
  const [detailEvent, setDetailEvent] = useState<Event | null>(null)

  const loadEvents = useCallback(async () => {
    try {
      const data = await api.getEvents()
      setEvents(data)
      setError(null)
    } catch {
      setError('Failed to load events. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadEvents()
  }, [loadEvents])

  const handleDateClick = (arg: DateClickArg) => {
    setFormModal({ mode: 'create', defaultStart: arg.dateStr })
  }

  const handleEventClick = (arg: EventClickArg) => {
    const event = events.find((e) => e.id === Number(arg.event.id))
    if (event) setDetailEvent(event)
  }

  const handleCreate = async (data: EventCreate | EventUpdate) => {
    await api.createEvent(data as EventCreate)
    await loadEvents()
    setFormModal(null)
  }

  const handleUpdate = async (id: number, data: EventCreate | EventUpdate) => {
    await api.updateEvent(id, data as EventUpdate)
    await loadEvents()
    setFormModal(null)
    setDetailEvent(null)
  }

  const handleDelete = async (id: number) => {
    await api.deleteEvent(id)
    await loadEvents()
    setDetailEvent(null)
  }

  const handleCancel = async (id: number) => {
    const updated = await api.cancelEvent(id)
    setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)))
    setDetailEvent(updated)
  }

  // Convert our events to the format FullCalendar expects
  const calendarEvents = events.map((e) => ({
    id: String(e.id),
    title: e.title,
    start: e.start_datetime,
    end: e.end_datetime,
    classNames: e.status === 'cancelled' ? ['event-cancelled'] : [],
    extendedProps: e,
  }))

  return (
    <div className="app">
      <header className="header">
        <h1>&#128197; Mini Calendar</h1>
        <div className="header-actions">
          <button className="btn-theme" onClick={toggle} title="Toggle theme">
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          <button
            className="btn btn-primary"
            onClick={() => setFormModal({ mode: 'create', defaultStart: '' })}
          >
            + New Event
          </button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="calendar-wrapper">
        {loading ? (
          <div className="loading">Loading events…</div>
        ) : (
          <FullCalendar
            plugins={[dayGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            events={calendarEvents}
            dateClick={handleDateClick}
            eventClick={handleEventClick}
            height="auto"
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: '',
            }}
            eventDisplay="block"
          />
        )}
      </main>

      {formModal && (
        <EventFormModal
          mode={formModal.mode}
          event={formModal.mode === 'edit' ? formModal.event : undefined}
          defaultStart={formModal.mode === 'create' ? formModal.defaultStart : undefined}
          onSubmit={
            formModal.mode === 'edit'
              ? (data) => handleUpdate(formModal.event.id, data)
              : handleCreate
          }
          onClose={() => setFormModal(null)}
        />
      )}

      {detailEvent && (
        <EventDetailModal
          event={detailEvent}
          onEdit={() => {
            setFormModal({ mode: 'edit', event: detailEvent })
            setDetailEvent(null)
          }}
          onDelete={() => handleDelete(detailEvent.id)}
          onCancel={() => handleCancel(detailEvent.id)}
          onClose={() => setDetailEvent(null)}
        />
      )}
    </div>
  )
}
