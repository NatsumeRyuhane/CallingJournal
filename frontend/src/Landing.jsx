/**
 * Landing.jsx
 * Marketing and home page for the Journal AI application
 * 
 * Author: Haider Amin
 * 
 * This page includes:
 * - Hero section with main call-to-action
 * - Feature highlights (Voice Journaling, Visual Calendar, AI Insights)
 * - User testimonials with ratings
 * - Pricing plans (Free, Pro, Enterprise)
 * - Navigation bar with login button
 */

import { useState } from 'react'

const Landing = ({ onLogin }) => {
  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-blue-900 to-purple-900">
      {/* Navigation */}
      <nav className="border-b border-purple-700/30 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span className="text-2xl font-light text-white">Journal AI</span>
            </div>
            <button
              onClick={onLogin}
              className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-md font-light transition-colors"
            >
              Login
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl sm:text-6xl font-light text-white mb-6">
            Your AI-Powered
            <br />
            <span className="text-purple-400">Personal Journal</span>
          </h1>
          <p className="text-xl font-light text-gray-300 mb-8 max-w-2xl mx-auto">
            Capture your thoughts through voice or text. Let AI help you reflect, 
            organize, and grow through the power of journaling.
          </p>
          <button
            onClick={onLogin}
            className="bg-purple-600 hover:bg-purple-500 text-white px-8 py-3 rounded-lg text-lg font-light transition-colors shadow-lg"
          >
            Start Journaling Free
          </button>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
            </div>
            <h3 className="text-xl font-light text-white mb-2">Voice Journaling</h3>
            <p className="text-sm font-light text-gray-400">
              Speak naturally and let AI transcribe your thoughts into beautiful journal entries
            </p>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-light text-white mb-2">Visual Calendar</h3>
            <p className="text-sm font-light text-gray-400">
              See your entire year at a glance with beautiful visual indicators for each entry
            </p>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-light text-white mb-2">AI Insights</h3>
            <p className="text-sm font-light text-gray-400">
              Get personalized insights and reflections powered by advanced AI technology
            </p>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="bg-slate-900/50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-light text-white text-center mb-12">
            What Our Users Say
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                  SJ
                </div>
                <div className="ml-3">
                  <h4 className="text-white font-light">Sarah Johnson</h4>
                  <p className="text-sm text-gray-400 font-light">Life Coach</p>
                </div>
              </div>
              <p className="text-sm font-light text-gray-300 leading-relaxed">
                "Journal AI has transformed how I reflect on my day. The voice feature makes it so easy to capture thoughts on the go!"
              </p>
              <div className="mt-4 text-yellow-400">★★★★★</div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                  MK
                </div>
                <div className="ml-3">
                  <h4 className="text-white font-light">Michael Kim</h4>
                  <p className="text-sm text-gray-400 font-light">Entrepreneur</p>
                </div>
              </div>
              <p className="text-sm font-light text-gray-300 leading-relaxed">
                "The calendar view helps me stay consistent with my journaling practice. I can see my progress at a glance!"
              </p>
              <div className="mt-4 text-yellow-400">★★★★★</div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                  EC
                </div>
                <div className="ml-3">
                  <h4 className="text-white font-light">Emily Chen</h4>
                  <p className="text-sm text-gray-400 font-light">Student</p>
                </div>
              </div>
              <p className="text-sm font-light text-gray-300 leading-relaxed">
                "Finally, a journaling app that understands me. The AI features are mind-blowing and actually helpful!"
              </p>
              <div className="mt-4 text-yellow-400">★★★★★</div>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-light text-white text-center mb-12">
          Simple, Transparent Pricing
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Free Plan */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-8">
            <h3 className="text-2xl font-light text-white mb-2">Free</h3>
            <div className="mb-6">
              <span className="text-4xl font-light text-white">$0</span>
              <span className="text-gray-400 font-light">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                30 journal entries per month
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Basic voice transcription
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Calendar view
              </li>
            </ul>
            <button
              onClick={onLogin}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white py-2 px-4 rounded-md font-light transition-colors"
            >
              Get Started
            </button>
          </div>

          {/* Pro Plan */}
          <div className="bg-purple-600/20 backdrop-blur-sm border-2 border-purple-500 rounded-lg p-8 relative">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-light">
              Most Popular
            </div>
            <h3 className="text-2xl font-light text-white mb-2">Pro</h3>
            <div className="mb-6">
              <span className="text-4xl font-light text-white">$9</span>
              <span className="text-gray-400 font-light">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Unlimited journal entries
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Advanced AI transcription
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                AI insights & analytics
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Export to PDF
              </li>
            </ul>
            <button
              onClick={onLogin}
              className="w-full bg-purple-600 hover:bg-purple-500 text-white py-2 px-4 rounded-md font-light transition-colors"
            >
              Start Free Trial
            </button>
          </div>

          {/* Enterprise Plan */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-700/30 rounded-lg p-8">
            <h3 className="text-2xl font-light text-white mb-2">Enterprise</h3>
            <div className="mb-6">
              <span className="text-4xl font-light text-white">$29</span>
              <span className="text-gray-400 font-light">/month</span>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Everything in Pro
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Priority support
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Custom integrations
              </li>
              <li className="flex items-start gap-2 text-sm font-light text-gray-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Team collaboration
              </li>
            </ul>
            <button
              onClick={onLogin}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white py-2 px-4 rounded-md font-light transition-colors"
            >
              Contact Sales
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-purple-700/30 bg-slate-900/50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm font-light text-gray-400">
            © 2025 Journal AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Landing