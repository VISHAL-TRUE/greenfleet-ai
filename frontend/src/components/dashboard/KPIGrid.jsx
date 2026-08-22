import React from 'react'
import { Truck, Fuel, CloudFog, Activity, TrendingDown } from 'lucide-react'
import MetricCard from '../common/MetricCard.jsx'

export default function KPIGrid() {
  const kpiData = [
    {
      id: 'active-vehicles',
      label: 'Active Vehicles',
      value: '42',
      unit: 'Units',
      icon: Truck,
      subtitle: '38 on route, 4 standby',
      accent: 'emerald',
    },
    {
      id: 'fuel-consumption',
      label: 'Fuel Consumption',
      value: '1,497',
      unit: 'L',
      icon: Fuel,
      trend: '-18.7%',
      trendPositive: true,
      subtitle: 'vs baseline',
      accent: 'cyan',
    },
    {
      id: 'estimated-co2',
      label: 'Estimated CO₂',
      value: '3.9',
      unit: 't',
      icon: CloudFog,
      trend: '-0.9 t',
      trendPositive: true,
      subtitle: 'reduced today',
      accent: 'emerald',
    },
    {
      id: 'fleet-utilisation',
      label: 'Fleet Utilisation',
      value: '87%',
      icon: Activity,
      trend: '+16%',
      trendPositive: true,
      subtitle: 'optimal load',
      accent: 'blue',
    },
    {
      id: 'fuel-saved',
      label: 'Fuel Saved',
      value: '345',
      unit: 'L',
      icon: TrendingDown,
      trend: '₹31,050',
      trendPositive: true,
      subtitle: 'cost delta',
      accent: 'amber',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      {kpiData.map((kpi) => (
        <MetricCard
          key={kpi.id}
          label={kpi.label}
          value={kpi.value}
          unit={kpi.unit}
          icon={kpi.icon}
          trend={kpi.trend}
          trendPositive={kpi.trendPositive}
          subtitle={kpi.subtitle}
          accent={kpi.accent}
        />
      ))}
    </div>
  )
}
