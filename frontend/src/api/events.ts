import axios from 'axios'
import type { Event, EventCreate, EventUpdate } from '../types/event'

const api = axios.create()

export async function getEvents(): Promise<Event[]> {
  const { data } = await api.get<Event[]>('/api/events')
  return data
}

export async function createEvent(payload: EventCreate): Promise<Event> {
  const { data } = await api.post<Event>('/api/events', payload)
  return data
}

export async function updateEvent(id: number, payload: EventUpdate): Promise<Event> {
  const { data } = await api.put<Event>(`/api/events/${id}`, payload)
  return data
}

export async function deleteEvent(id: number): Promise<void> {
  await api.delete(`/api/events/${id}`)
}

export async function cancelEvent(id: number): Promise<Event> {
  const { data } = await api.patch<Event>(`/api/events/${id}/cancel`)
  return data
}
