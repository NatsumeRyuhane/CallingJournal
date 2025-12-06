/**
 * Calendar.jsx
 * Year-at-a-glance calendar view with journal entry management
 * 
 * Author: Haider Amin
 * 
 * This component displays:
 * - All 12 months in a 4x3 grid layout
 * - Visual indicators for journal entries (green = entry, gray = no entry)
 * - Future date protection (grayed out and disabled)
 * - Left sidebar panel for viewing and managing entries
 * - Entry management features (star, hide, remove with confirmation)
 * - Profile menu for user settings and logout
 */

import { useState } from 'react'
import ProfileMenu from './ProfileMenu'

const Calendar = ({ onOpenAITalk, onLogout, onBackToChat }) => {
  // Sample journal data - in a real app, this would come from an API or local storage
  const [journalEntries, setJournalEntries] = useState(new Set([
    '2025-01-15', '2025-01-20', '2025-02-05', '2025-02-14', '2025-02-28',
    '2025-03-10', '2025-03-22', '2025-04-03', '2025-04-18', '2025-05-01',
    '2025-05-12', '2025-06-08', '2025-06-25', '2025-07-04', '2025-07-19',
    '2025-08-11', '2025-08-30', '2025-09-15', '2025-10-07', '2025-10-31',
    '2025-11-03', '2025-11-15', '2025-12-10', '2025-12-25'
  ]))

  // Dummy journal content
  const journalData = {
    '2025-01-15': { title: 'New Year Goals', mood: '😊', duration: '25 min', content: 'Started the year with renewed energy. Set ambitious goals for health and career.' },
    '2025-02-14': { title: 'Valentine\'s Day Reflections', mood: '❤️', duration: '15 min', content: 'Reflected on relationships and gratitude. Spent quality time with loved ones.' },
    '2025-03-22': { title: 'Spring Has Arrived', mood: '🌸', duration: '20 min', content: 'Noticed the first signs of spring. Feeling refreshed and motivated.' },
    '2025-05-01': { title: 'May Day Adventures', mood: '🎉', duration: '30 min', content: 'Celebrated new beginnings. Started a new creative project.' },
    '2025-11-03': { title: 'Today\'s Session', mood: '✨', duration: '18 min', content: 'Working on my journaling app. Excited about the progress made today.' },
  }

  const [selectedDate, setSelectedDate] = useState(null)
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [showManageMenu, setShowManageMenu] = useState(false)
  const [showDeleteWarning, setShowDeleteWarning] = useState(false)
  const [starredEntries, setStarredEntries] = useState(new Set())
  const [hiddenEntries, setHiddenEntries] = useState(new Set())

  const currentYear = 2025
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (year, month) => {
    return new Date(year, month, 1).getDay()
  }

  const formatDate = (year, month, day) => {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  const hasJournalEntry = (year, month, day) => {
    const dateStr = formatDate(year, month, day)
    return journalEntries.has(dateStr)
  }

  const toggleJournalEntry = (year, month, day) => {
    const dateStr = formatDate(year, month, day)
    const newEntries = new Set(journalEntries)
    
    if (newEntries.has(dateStr)) {
      newEntries.delete(dateStr)
    } else {
      newEntries.add(dateStr)
    }
    
    setJournalEntries(newEntries)
  }

  const handleDateClick = (year, month, day) => {
    const dateStr = formatDate(year, month, day)
    setSelectedDate(dateStr)
    setIsPanelOpen(true)
    setShowManageMenu(false)
    setShowDeleteWarning(false)
  }

  const formatDisplayDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
  }

  const handleToggleStar = () => {
    const newStarred = new Set(starredEntries)
    if (newStarred.has(selectedDate)) {
      newStarred.delete(selectedDate)
    } else {
      newStarred.add(selectedDate)
    }
    setStarredEntries(newStarred)
    setShowManageMenu(false)
  }

  const handleToggleHidden = () => {
    const newHidden = new Set(hiddenEntries)
    if (newHidden.has(selectedDate)) {
      newHidden.delete(selectedDate)
    } else {
      newHidden.add(selectedDate)
    }
    setHiddenEntries(newHidden)
    setShowManageMenu(false)
  }

  const handleDeleteEntry = () => {
    const newEntries = new Set(journalEntries)
    newEntries.delete(selectedDate)
    setJournalEntries(newEntries)
    
    // Also remove from starred and hidden
    const newStarred = new Set(starredEntries)
    newStarred.delete(selectedDate)
    setStarredEntries(newStarred)
    
    const newHidden = new Set(hiddenEntries)
    newHidden.delete(selectedDate)
    setHiddenEntries(newHidden)
    
    setShowDeleteWarning(false)
    setShowManageMenu(false)
    setIsPanelOpen(false)
  }

  const renderMonth = (monthIndex) => {
    const daysInMonth = getDaysInMonth(currentYear, monthIndex)
    const firstDay = getFirstDayOfMonth(currentYear, monthIndex)
    const days = []
    
    const today = new Date()
    today.setHours(0, 0, 0, 0) // Reset time to start of day for accurate comparison

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(
        <div key={`empty-${i}`} className="h-5 w-5"></div>
      )
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const hasEntry = hasJournalEntry(currentYear, monthIndex, day)
      const currentDate = new Date(currentYear, monthIndex, day)
      currentDate.setHours(0, 0, 0, 0)
      const isToday = today.toDateString() === currentDate.toDateString()
      const isFuture = currentDate > today
      
      days.push(
        <button
          key={day}
          onClick={() => !isFuture && handleDateClick(currentYear, monthIndex, day)}
          disabled={isFuture}
          className={`
            h-5 w-5 rounded text-[10px] font-light transition-all duration-200
            ${isFuture 
              ? 'bg-slate-800/30 text-slate-600 cursor-not-allowed' 
              : hasEntry 
                ? 'bg-emerald-500 text-white shadow-sm hover:bg-emerald-400 cursor-pointer hover:scale-110' 
                : 'bg-slate-700 text-gray-300 hover:bg-slate-600 border border-slate-600 hover:scale-110'
            }
            ${isToday ? 'ring-1 ring-purple-400' : ''}
          `}
        >
          {day}
        </button>
      )
    }

    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-md shadow-sm border border-purple-700/30 p-2">
        <h3 className="text-xs font-light text-white mb-1 text-center">
          {months[monthIndex]}
        </h3>
        
        {/* Days of week header */}
        <div className="grid grid-cols-7 gap-0.5 mb-0.5">
          {daysOfWeek.map(day => (
            <div key={day} className="h-5 w-5 text-[9px] font-light text-purple-300 flex items-center justify-center">
              {day[0]}
            </div>
          ))}
        </div>
        
        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-0.5">
          {days}
        </div>
      </div>
    )
  }

  const totalEntries = journalEntries.size
  
  const hasEntry = selectedDate && journalEntries.has(selectedDate)
  const selectedJournalData = selectedDate && journalData[selectedDate] 
    ? journalData[selectedDate]
    : { title: 'Journal Entry', mood: '📝', duration: 'N/A', content: 'No details available for this entry yet.' }

  return (
    <div className="h-screen bg-linear-to-br from-slate-900 via-blue-900 to-purple-900 flex overflow-hidden font-['Inter',sans-serif]">
      {/* Left Sidebar Panel */}
      <div className={`bg-slate-800 shadow-2xl transition-all duration-300 ease-in-out ${isPanelOpen ? 'w-80' : 'w-0'} overflow-hidden border-r border-purple-700/30`}>
        <div className="h-full flex flex-col p-6 relative">
          {/* Close button - inside panel */}
          {isPanelOpen && (
            <button 
              onClick={() => setIsPanelOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl transition-colors z-10"
            >
              ×
            </button>
          )}
          
          {selectedDate && (
            <>
              {hasEntry ? (
                <>
                  <div className="mb-4">
                    <h2 className="text-2xl font-light text-white mb-1">
                      {selectedJournalData.title}
                    </h2>
                    <p className="text-sm font-light text-purple-300">
                      {formatDisplayDate(selectedDate)}
                    </p>
                  </div>

                  <div className="flex gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{selectedJournalData.mood}</span>
                      <span className="text-xs font-light text-gray-400">Mood</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-light text-white">{selectedJournalData.duration}</span>
                      <span className="text-xs font-light text-gray-400">Duration</span>
                    </div>
                  </div>

                  {/* Audio Playback Controls */}
                  <div className="mb-4 bg-slate-900/50 rounded-lg p-3 border border-purple-700/30">
                    <div className="flex items-center gap-3 mb-2">
                      <button className="w-8 h-8 rounded-full bg-purple-600 hover:bg-purple-500 transition-colors flex items-center justify-center text-white">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M8 5v14l11-7z"/>
                        </svg>
                      </button>
                      <div className="flex-1">
                        <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-500 rounded-full" style={{width: '35%'}}></div>
                        </div>
                      </div>
                      <span className="text-xs font-light text-gray-400">1:23</span>
                    </div>
                    <div className="flex items-center justify-between text-xs font-light text-gray-400">
                      <span>🎤 AI Voice Journal</span>
                      <button className="hover:text-purple-400 transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div className="flex-1 overflow-y-auto">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-medium text-gray-300">Entry</h3>
                      {starredEntries.has(selectedDate) && (
                        <span className="text-yellow-400 text-sm">⭐</span>
                      )}
                      {hiddenEntries.has(selectedDate) && (
                        <span className="text-gray-500 text-xs">(Hidden)</span>
                      )}
                    </div>
                    <p className="text-sm font-light text-gray-300 leading-relaxed">
                      {selectedJournalData.content}
                    </p>
                  </div>

                  <div className="mt-4 pt-4 border-t border-purple-700/30 space-y-2">
                    {/* Manage Entry Button with Dropdown */}
                    <div className="relative">
                      <button 
                        onClick={() => setShowManageMenu(!showManageMenu)}
                        className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-500 transition-colors text-sm font-light flex items-center justify-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                        </svg>
                        Manage Entry
                      </button>

                      {/* Dropdown Menu */}
                      {showManageMenu && (
                        <div className="absolute bottom-full left-0 right-0 mb-2 bg-slate-900 border border-purple-700/30 rounded-md shadow-xl overflow-hidden z-10">
                          <button
                            onClick={handleToggleStar}
                            className="w-full px-4 py-2.5 text-left text-sm font-light text-white hover:bg-slate-800 transition-colors flex items-center gap-3"
                          >
                            <span className="text-base">
                              {starredEntries.has(selectedDate) ? '⭐' : '☆'}
                            </span>
                            {starredEntries.has(selectedDate) ? 'Unstar Entry' : 'Star Entry'}
                          </button>
                          <button
                            onClick={handleToggleHidden}
                            className="w-full px-4 py-2.5 text-left text-sm font-light text-white hover:bg-slate-800 transition-colors flex items-center gap-3"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              {hiddenEntries.has(selectedDate) ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                              )}
                            </svg>
                            {hiddenEntries.has(selectedDate) ? 'Unhide Entry' : 'Hide Entry'}
                          </button>
                          <button
                            onClick={() => {
                              setShowManageMenu(false)
                              setShowDeleteWarning(true)
                            }}
                            className="w-full px-4 py-2.5 text-left text-sm font-light text-red-400 hover:bg-slate-800 transition-colors flex items-center gap-3"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Remove Entry
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Delete Warning Modal */}
                    {showDeleteWarning && (
                      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-20">
                        <div className="bg-slate-900 border-2 border-red-500/50 rounded-lg p-6 max-w-sm">
                          <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                              </svg>
                            </div>
                            <h3 className="text-lg font-light text-white">Remove Entry?</h3>
                          </div>
                          <p className="text-sm font-light text-gray-300 mb-6">
                            This will permanently delete this journal entry. This action cannot be undone.
                          </p>
                          <div className="flex gap-3">
                            <button
                              onClick={() => setShowDeleteWarning(false)}
                              className="flex-1 bg-slate-700 text-white py-2 px-4 rounded-md hover:bg-slate-600 transition-colors text-sm font-light"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={handleDeleteEntry}
                              className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors text-sm font-light"
                            >
                              Remove
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    <button 
                      onClick={() => onOpenAITalk && onOpenAITalk(selectedDate)}
                      className="w-full bg-slate-700 text-gray-300 py-2 px-4 rounded-md hover:bg-slate-600 transition-colors text-sm font-light flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                      </svg>
                      Talk to AI
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-6">
                    <h2 className="text-2xl font-light text-white mb-1">
                      New Entry
                    </h2>
                    <p className="text-sm font-light text-purple-300">
                      {formatDisplayDate(selectedDate)}
                    </p>
                  </div>

                  <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
                    <div className="w-16 h-16 rounded-full bg-purple-600/20 flex items-center justify-center mb-4">
                      <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-light text-white mb-2">Create an Entry</h3>
                    <p className="text-sm font-light text-gray-400 mb-6 max-w-xs">
                      Write or speak to capture your thoughts for this day
                    </p>
                  </div>

                  <div className="space-y-2">
                    <button 
                      onClick={() => {
                        const newEntries = new Set(journalEntries)
                        newEntries.add(selectedDate)
                        setJournalEntries(newEntries)
                        onOpenAITalk && onOpenAITalk(selectedDate)
                      }}
                      className="w-full bg-purple-600 text-white py-2.5 px-4 rounded-md hover:bg-purple-500 transition-colors text-sm font-light flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Create Entry
                    </button>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-[1400px] mx-auto relative">
          {/* Back Button - Fixed Position Left */}
          <div className="absolute top-0 left-0 z-30">
            <button
              onClick={onBackToChat}
              className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-md transition-colors font-light flex items-center gap-2 border border-purple-700/30"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Chat
            </button>
          </div>
          
          {/* Profile Menu - Fixed Position */}
          <div className="absolute top-0 right-0 z-30">
            <ProfileMenu onLogout={onLogout} />
          </div>

          {/* Header */}
          <div className="text-center mb-4">
            <h1 className="text-2xl font-light text-white mb-1">
              Journal Calendar {currentYear}
            </h1>
            <p className="text-sm font-light text-purple-200 mb-2">
              Track your daily journaling progress
            </p>
            <div className="flex flex-wrap justify-center items-center gap-3 text-xs font-light text-purple-200">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 bg-emerald-500 rounded shadow"></div>
                <span>Journal Entry ({totalEntries})</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 bg-slate-700 border border-slate-600 rounded"></div>
                <span>No Entry</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 bg-slate-800/30 border border-slate-700 rounded"></div>
                <span>Future Date</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 bg-slate-700 ring-1 ring-purple-400 rounded"></div>
                <span>Today</span>
              </div>
            </div>
          </div>

          {/* Calendar Grid - All 12 months in a 4x3 grid */}
          <div className="grid grid-cols-4 gap-3">
            {months.map((month, index) => (
              <div key={month}>
                {renderMonth(index)}
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="text-center mt-3 text-xs text-purple-300">
            <p>Click green days to view entries • Click gray days to add entries</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Calendar