import React from 'react'
import Header from './components/common/Header.jsx'
import Dashboard from './components/dashboard/Dashboard.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-[#070b13] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
      {/* Top Header */}
      <Header />

      {/* Operator Dashboard Container */}
      <div className="flex-1 pb-8">
        <Dashboard />
      </div>
    </div>
  )
}
