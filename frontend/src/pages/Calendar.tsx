import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import { eventsApi } from '../services/api'

export default function Calendar() {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)

  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn: () => eventsApi.list().then((res) => res.data),
  })

  const calendarEvents = (events || []).map((event: any) => ({
    id: event.id,
    title: event.title,
    start: event.start_time,
    end: event.end_time,
    backgroundColor: getEventColor(event.event_type),
    borderColor: getEventColor(event.event_type),
    extendedProps: {
      description: event.description,
      location: event.location,
      type: event.event_type,
    },
  }))

  const handleDateClick = (arg: any) => {
    setSelectedDate(arg.date)
    // TODO: Open modal to create new event
  }

  const handleEventClick = (arg: any) => {
    // TODO: Open modal to view/edit event
    console.log('Event clicked:', arg.event)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Calendar</h1>
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition">
          New Event
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
          }}
          events={calendarEvents}
          dateClick={handleDateClick}
          eventClick={handleEventClick}
          editable={true}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={true}
          weekends={true}
          slotMinTime="06:00:00"
          slotMaxTime="24:00:00"
          height="auto"
        />
      </div>
    </div>
  )
}

function getEventColor(type: string): string {
  const colors: Record<string, string> = {
    class: '#3b82f6',
    exam: '#ef4444',
    assignment: '#f59e0b',
    meeting: '#8b5cf6',
    social: '#ec4899',
    gym: '#10b981',
    meal: '#14b8a6',
    study: '#6366f1',
    other: '#6b7280',
  }
  return colors[type] || colors.other
}

