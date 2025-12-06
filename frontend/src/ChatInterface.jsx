/**
 * ChatInterface.jsx
 * Main chat interface with AI assistant for journaling
 * 
 * Author: Haider Amin
 * 
 * This component provides:
 * - AI chatbot interface for conversational journaling
 * - Header with AI insights and positive reinforcement
 * - Left sidebar with chat history organized by date
 * - Navigation to calendar view
 * - Message input with send functionality
 */

import { useState } from 'react'
import ProfileMenu from './ProfileMenu'

const ChatInterface = ({ onNavigateToCalendar, onLogout, onStartNewJournal }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hello! I'm your AI journaling assistant. How are you feeling today? Would you like to reflect on something?",
      timestamp: new Date(),
      showSuggestions: true
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isMenuCollapsed, setIsMenuCollapsed] = useState(false)

  // Dummy chat history organized by date
  const chatHistory = [
    {
      date: 'Today',
      chats: [
        { id: 1, title: 'Morning Reflection', time: '9:30 AM', active: true },
        { id: 2, title: 'Piano Practice Thoughts', time: '2:15 PM', active: false }
      ]
    },
    {
      date: 'Yesterday',
      chats: [
        { id: 3, title: 'Evening Gratitude', time: '8:45 PM', active: false },
        { id: 4, title: 'Work Day Review', time: '5:30 PM', active: false }
      ]
    },
    {
      date: 'This Week',
      chats: [
        { id: 5, title: 'Weekend Plans', time: 'Nov 4', active: false },
        { id: 6, title: 'Career Reflections', time: 'Nov 3', active: false },
        { id: 7, title: 'Family Time', time: 'Nov 2', active: false }
      ]
    }
  ]

  // Dummy AI insights
  const aiInsights = [
    "You've been on fire practicing the piano! Keep it going! 🎹",
    "Your consistency this week is amazing! 7 days in a row! 🌟",
    "I notice you're reflecting more on gratitude lately. Beautiful! 💫",
    "Your mindfulness practice is really developing! Keep it up! 🧘"
  ]

  const [currentInsight] = useState(aiInsights[0])

  // Suggestion buttons that appear after AI messages
  const suggestions = [
    "Start a new journal",
    "How was my day?",
    "Reflect on my goals",
    "Practice gratitude"
  ]

  const handleSuggestionClick = (suggestion) => {
    // Special handling for "Start a new journal"
    if (suggestion === "Start a new journal") {
      onStartNewJournal && onStartNewJournal()
      return
    }
    setInputMessage(suggestion)
  }

  const handleSendMessage = (customMessage = null) => {
    const messageToSend = customMessage || inputMessage
    if (messageToSend.trim() === '') return

    const newMessage = {
      id: messages.length + 1,
      role: 'user',
      content: messageToSend,
      timestamp: new Date()
    }

    setMessages([...messages, newMessage])
    setInputMessage('')

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        role: 'assistant',
        content: "That's a wonderful reflection! Tell me more about how that made you feel.",
        timestamp: new Date(),
        showSuggestions: Math.random() > 0.5 // Randomly show suggestions
      }
      setMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="h-screen bg-linear-to-br from-slate-900 via-blue-900 to-purple-900 flex overflow-hidden">
      {/* Left Sidebar - Chat History */}
      <div className={`bg-slate-800 border-r border-purple-700/30 flex flex-col transition-all duration-300 ${isMenuCollapsed ? 'w-16' : 'w-80'}`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-purple-700/30">
          {!isMenuCollapsed ? (
            <>
              <h2 className="text-xl font-light text-white mb-4">Journal Chats</h2>
              <button className="w-full bg-purple-600 hover:bg-purple-500 text-white py-2.5 px-4 rounded-md transition-colors font-light flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                </svg>
                New Chat
              </button>
            </>
          ) : (
            <button className="w-full bg-purple-600 hover:bg-purple-500 text-white p-2 rounded-md transition-colors">
              <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          )}
        </div>

        {/* Chat History List */}
        <div className="flex-1 overflow-y-auto p-4">
          {!isMenuCollapsed ? (
            chatHistory.map((section) => (
              <div key={section.date} className="mb-6">
                <h3 className="text-xs font-light text-gray-400 uppercase mb-2 px-2">
                  {section.date}
                </h3>
                <div className="space-y-1">
                  {section.chats.map((chat) => (
                    <button
                      key={chat.id}
                      className={`w-full text-left px-3 py-2.5 rounded-md transition-colors ${
                        chat.active
                          ? 'bg-purple-600/20 text-white border border-purple-500/30'
                          : 'text-gray-300 hover:bg-slate-700'
                      }`}
                    >
                      <div className="font-light text-sm truncate">{chat.title}</div>
                      <div className="text-xs font-light text-gray-400 mt-0.5">{chat.time}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="space-y-2">
              {chatHistory.flatMap(section => section.chats).map((chat) => (
                <button
                  key={chat.id}
                  className={`w-full p-2 rounded-md transition-colors ${
                    chat.active
                      ? 'bg-purple-600/20 text-white'
                      : 'text-gray-300 hover:bg-slate-700'
                  }`}
                  title={chat.title}
                >
                  <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Calendar Navigation & Toggle */}
        <div className="p-4 border-t border-purple-700/30 space-y-2">
          {!isMenuCollapsed ? (
            <>
              <button
                onClick={onNavigateToCalendar}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white py-2.5 px-4 rounded-md transition-colors font-light flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Calendar View
              </button>
              <button
                onClick={() => setIsMenuCollapsed(true)}
                className="w-full text-gray-400 hover:text-white py-2 text-sm font-light flex items-center justify-center gap-2 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
                Collapse
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onNavigateToCalendar}
                className="w-full bg-slate-700 hover:bg-slate-600 text-white p-2 rounded-md transition-colors"
                title="Calendar View"
              >
                <svg className="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>
              <button
                onClick={() => setIsMenuCollapsed(false)}
                className="w-full text-gray-400 hover:text-white p-2 transition-colors"
                title="Expand"
              >
                <svg className="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header with AI Insight */}
        <div className="bg-slate-900/50 backdrop-blur-sm border-b border-purple-700/30 p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-10 h-10 rounded-full bg-linear-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div className="flex-1">
                <div className="text-xs font-light text-purple-300 uppercase">AI Insight</div>
                <div className="text-sm font-light text-white">{currentInsight}</div>
              </div>
            </div>
            <ProfileMenu onLogout={onLogout} />
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div key={message.id}>
                <div
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-800 text-gray-200 border border-purple-700/30'
                    }`}
                  >
                    <p className="text-sm font-light leading-relaxed">{message.content}</p>
                    <p className="text-xs font-light opacity-60 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
                
                {/* Suggestion Buttons - show after assistant messages */}
                {message.role === 'assistant' && message.showSuggestions && index === messages.length - 1 && (
                  <div className="flex flex-wrap gap-2 mt-3 ml-2">
                    {suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white px-4 py-2 rounded-full text-sm font-light border border-purple-700/30 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-slate-900/50 backdrop-blur-sm border-t border-purple-700/30 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-3">
              <div className="flex-1 bg-slate-800 border border-purple-700/30 rounded-lg overflow-hidden">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share your thoughts, feelings, or reflections..."
                  className="w-full bg-transparent text-white font-light px-4 py-3 outline-none resize-none"
                  rows="3"
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={inputMessage.trim() === ''}
                className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white p-3 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            <div className="flex items-center gap-4 mt-3">
              <button className="text-gray-400 hover:text-white transition-colors font-light text-sm flex items-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                Voice Input
              </button>
              <span className="text-xs font-light text-gray-500">
                Press Enter to send, Shift+Enter for new line
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface