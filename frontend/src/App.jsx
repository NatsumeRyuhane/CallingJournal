/**
 * App.jsx
 * Main application component with routing and authentication
 * 
 * Author: Haider Amin
 */

import { useState } from 'react'
import Landing from './Landing'
import ChatInterface from './ChatInterface'
import Calendar from './Calendar'
import AITalk from './AITalk'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentPage, setCurrentPage] = useState('chat') // 'chat', 'calendar', or 'aitalk'

  const handleLogin = () => {
    setIsLoggedIn(true)
    setCurrentPage('chat')
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setCurrentPage('chat')
  }

  const handleNavigateToCalendar = () => {
    setCurrentPage('calendar')
  }

  const handleBackToChat = () => {
    setCurrentPage('chat')
  }

  const handleOpenAITalk = (date) => {
    setCurrentPage('aitalk')
  }

  const handleStartNewJournal = () => {
    setCurrentPage('aitalk')
  }

  if (!isLoggedIn) {
    return <Landing onLogin={handleLogin} />
  }

  if (currentPage === 'aitalk') {
    return <AITalk onBack={handleBackToChat} onLogout={handleLogout} />
  }

  if (currentPage === 'calendar') {
    return <Calendar onOpenAITalk={handleOpenAITalk} onLogout={handleLogout} onBackToChat={handleBackToChat} />
  }

  return <ChatInterface onNavigateToCalendar={handleNavigateToCalendar} onLogout={handleLogout} onStartNewJournal={handleStartNewJournal} />
}

export default App
