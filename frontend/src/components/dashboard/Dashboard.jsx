import React from 'react'
import KPIGrid from './KPIGrid.jsx'
import ActionBar from './ActionBar.jsx'
import FleetMapPlaceholder from './FleetMapPlaceholder.jsx'
import FleetStatus from './FleetStatus.jsx'
import AnalyticsPlaceholder from './AnalyticsPlaceholder.jsx'
import BeforeAfter from './BeforeAfter.jsx'

export default function Dashboard() {
  return (
    <main className="mx-auto w-full max-w-[1440px] px-4 sm:px-6 py-5 space-y-4">
      {/* 1. Primary Metrics Row */}
      <KPIGrid />

      {/* 2. Simulation & Optimization Action Bar */}
      <ActionBar />

      {/* 3. Main Network Map & Fleet Status Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        {/* Left / Large: Fleet & Route Network (8 of 12 cols on desktop) */}
        <div className="lg:col-span-8 flex flex-col min-h-[420px]">
          <FleetMapPlaceholder />
        </div>

        {/* Right / Narrow: Fleet Status (4 of 12 cols on desktop) */}
        <div className="lg:col-span-4 flex flex-col min-h-[420px]">
          <FleetStatus />
        </div>
      </div>

      {/* 4. Analytics Panels (Fuel Consumption Analysis & Fleet Efficiency) */}
      <AnalyticsPlaceholder />

      {/* 5. Comparative Evaluation: Baseline vs GreenFlow */}
      <BeforeAfter />
    </main>
  )
}
