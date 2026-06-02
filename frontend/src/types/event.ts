export interface Event {
  id: number
  title: string
  description: string | null
  location: string | null
  start_datetime: string
  end_datetime: string
  status: 'scheduled' | 'cancelled'
  created_at: string
  updated_at: string
}

export interface EventCreate {
  title: string
  description?: string
  location?: string
  start_datetime: string
  end_datetime: string
}

export interface EventUpdate {
  title?: string
  description?: string
  location?: string
  start_datetime?: string
  end_datetime?: string
}
