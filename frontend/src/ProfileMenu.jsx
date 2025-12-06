/**
 * ProfileMenu.jsx
 * User profile dropdown menu component
 * 
 * Author: Haider Amin
 * 
 * This reusable component provides:
 * - Circular profile button that opens a dropdown menu
 * - User information display (name and email)
 * - Navigation options (Profile, Settings, Help & Support)
 * - Logout functionality that returns to landing page
 * - Click-outside-to-close behavior
 */

import { useState } from 'react'

const ProfileMenu = ({ onLogout }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-10 h-10 rounded-full bg-purple-600 hover:bg-purple-500 transition-colors flex items-center justify-center text-white font-light shadow-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop to close menu */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-purple-700/30 rounded-lg shadow-xl overflow-hidden z-20">
            <div className="px-4 py-3 border-b border-purple-700/30">
              <p className="text-sm font-light text-white">John Doe</p>
              <p className="text-xs font-light text-gray-400">john@example.com</p>
            </div>

            <button
              onClick={() => {
                setIsOpen(false)
                // Navigate to profile (placeholder)
              }}
              className="w-full px-4 py-2.5 text-left text-sm font-light text-white hover:bg-slate-800 transition-colors flex items-center gap-3"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile
            </button>

            <button
              onClick={() => {
                setIsOpen(false)
                // Open settings (placeholder)
              }}
              className="w-full px-4 py-2.5 text-left text-sm font-light text-white hover:bg-slate-800 transition-colors flex items-center gap-3"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </button>

            <button
              onClick={() => {
                setIsOpen(false)
                // Open help (placeholder)
              }}
              className="w-full px-4 py-2.5 text-left text-sm font-light text-white hover:bg-slate-800 transition-colors flex items-center gap-3"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Help & Support
            </button>

            <div className="border-t border-purple-700/30">
              <button
                onClick={() => {
                  setIsOpen(false)
                  onLogout && onLogout()
                }}
                className="w-full px-4 py-2.5 text-left text-sm font-light text-red-400 hover:bg-slate-800 transition-colors flex items-center gap-3"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Log Out
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ProfileMenu