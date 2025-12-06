/**
 * AITalk.jsx
 * Journal entry editor with voice and text input capabilities
 * 
 * Author: Haider Amin
 * 
 * This page provides:
 * - Document-style text editor for writing journal entries
 * - Voice recording controls (mute, volume, end call)
 * - AI assistant status indicator
 * - Word count tracking
 * - Back navigation to calendar
 * - Integration of both typing and voice input methods
 */

import { useState } from 'react'
import ProfileMenu from './ProfileMenu'

const AITalk = ({ onBack, selectedDate, onLogout }) => {
  const [content, setContent] = useState('')
  const [isMuted, setIsMuted] = useState(false)
  const [volume, setVolume] = useState(50)
  const [isCallActive, setIsCallActive] = useState(true)

  const formatDisplayDate = (dateStr) => {
    if (!dateStr) return 'New Entry'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
  }

  const handleEndCall = () => {
    setIsCallActive(false)
    // Could add a confirmation dialog here
    setTimeout(() => onBack(), 500)
  }

  return (
    <div className="h-screen bg-linear-to-br from-slate-900 via-blue-900 to-purple-900 flex flex-col">
      {/* Header with back button */}
      <div className="flex items-center justify-between p-4 border-b border-purple-700/30">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-purple-200 hover:text-white transition-colors font-light"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Calendar
        </button>
        <div className="flex items-center gap-4">
          <div className="text-purple-200 font-light text-sm">
            {formatDisplayDate(selectedDate)}
          </div>
          <ProfileMenu onLogout={onLogout} />
        </div>
      </div>

      {/* Main Content - Document Editor */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-4xl mx-auto">
          {/* Document Paper */}
          <div className="bg-white rounded-lg shadow-2xl min-h-[700px] p-12">
            {/* Document Header */}
            <div className="mb-6 pb-4 border-b border-gray-200">
              <input
                type="text"
                placeholder="Entry Title"
                className="text-3xl font-light text-gray-900 w-full outline-none placeholder-gray-300"
                defaultValue="My Journal Entry"
              />
              <div className="text-sm font-light text-gray-500 mt-2">
                {formatDisplayDate(selectedDate)}
              </div>
            </div>

            {/* Document Content */}
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Start writing your thoughts... or speak with the AI to transcribe your journal entry."
              className="w-full min-h-[500px] text-base font-light text-gray-800 leading-relaxed outline-none resize-none placeholder-gray-300"
              style={{ fontFamily: 'Inter, sans-serif' }}
            />

            {/* Word Count */}
            <div className="mt-4 pt-4 border-t border-gray-200 text-sm font-light text-gray-400 text-right">
              {content.split(/\s+/).filter(word => word.length > 0).length} words
            </div>
          </div>
        </div>
      </div>

      {/* Call Controls Bar */}
      <div className="bg-slate-900/95 backdrop-blur-sm border-t border-purple-700/30 p-4">
        <div className="max-w-4xl mx-auto">
          {/* AI Status Indicator */}
          <div className="text-center mb-4">
            <div className="inline-flex items-center gap-2 text-purple-200 font-light text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              AI Assistant is listening...
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-center gap-6">
            {/* Mute/Unmute Button */}
            <button
              onClick={() => setIsMuted(!isMuted)}
              className={`w-14 h-14 rounded-full transition-all ${
                isMuted 
                  ? 'bg-red-500 hover:bg-red-600' 
                  : 'bg-slate-700 hover:bg-slate-600'
              } flex items-center justify-center text-white shadow-lg`}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              )}
            </button>

            {/* End Call Button */}
            <button
              onClick={handleEndCall}
              className="w-16 h-16 rounded-full bg-red-600 hover:bg-red-700 transition-all flex items-center justify-center text-white shadow-lg transform hover:scale-105"
              title="End Call"
            >
              <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08c-.18-.17-.29-.42-.29-.7 0-.28.11-.53.29-.71C3.34 8.78 7.46 7 12 7s8.66 1.78 11.71 4.67c.18.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.11-.7-.28-.79-.74-1.68-1.36-2.66-1.85-.33-.16-.56-.5-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
              </svg>
            </button>

            {/* Volume Control */}
            <div className="flex items-center gap-3 bg-slate-700 rounded-full px-4 py-3 shadow-lg">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(e) => setVolume(e.target.value)}
                className="w-24 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer accent-purple-500"
                title={`Volume: ${volume}%`}
              />
              <span className="text-white text-sm font-light w-8">{volume}%</span>
            </div>

            {/* Settings Button */}
            <button
              className="w-14 h-14 rounded-full bg-slate-700 hover:bg-slate-600 transition-all flex items-center justify-center text-white shadow-lg"
              title="Settings"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>

          {/* Additional Info */}
          <div className="text-center mt-4 text-xs font-light text-gray-400">
            Speak naturally and the AI will help transcribe and organize your thoughts
          </div>
        </div>
      </div>
    </div>
  )
}

export default AITalk