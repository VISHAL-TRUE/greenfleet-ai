import React from 'react'
import { Truck, Fuel, CloudFog, Activity, TrendingDown } from 'lucide-react'
import MetricCard from '../common/MetricCard.jsx'

export default function KPIGrid({
  benchmark = null,
  simulationState = null,
  isOptimized = false,
}) {
  const totalVehicles = simulationState?.vehicles?.length || 0
  const totalRoutes = simulationState?.routes?.length || 0
  const activeAssignments = isOptimized
    ? simulationState?.greenflow_assignments || []
    : simulationState?.baseline_assignments || []
  const assignedCount = activeAssignments.length
  const standbyCount = Math.max(0, totalVehicles - assignedCount)

  const baselineData = benchmark?.baseline
  const greenflowData = benchmark?.greenflow

  const kpiData = [
    {
      id: 'active-vehicles',
      label: 'Active Vehicles',
      value: assignedCount.toString(),
      unit: `/ ${totalVehicles}`,
      icon: Truck,
      subtitle: `${standbyCount} standby in depot`,
      accent: 'emerald',
    },
    {
      id: 'fuel-consumption',
      label: 'Fuel Consumption',
      value: isOptimized && greenflowData
        ? greenflowData.total_fuel_l.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
        : (baselineData?.total_fuel_l?.toFixed(1) || '--'),
      unit: 'L',
      icon: Fuel,
      trend: isOptimized && benchmark ? `-${benchmark.fuel_saved_pct.toFixed(1)}%` : null,
      trendPositive: true,
      subtitle: isOptimized && baselineData
        ? `Baseline: ${baselineData.total_fuel_l.toFixed(1)} L`
        : 'Uncoordinated baseline',
      accent: 'cyan',
    },
    {
      id: 'estimated-co2',
      label: 'Estimated CO₂',
      value: isOptimized && greenflowData
        ? (greenflowData.estimated_co2_kg / 1000).toFixed(2)
        : baselineData
        ? (baselineData.estimated_co2_kg / 1000).toFixed(2)
        : '--',
      unit: 't',
      icon: CloudFog,
      trend: isOptimized && benchmark ? `-${(benchmark.co2_reduced_kg / 1000).toFixed(2)} t` : null,
      trendPositive: true,
      subtitle: isOptimized && benchmark
        ? `Reduced by ${benchmark.co2_reduced_pct.toFixed(1)}%`
        : 'Direct fleet emissions',
      accent: 'emerald',
    },
    {
      id: 'fleet-utilisation',
      label: 'Fleet Utilisation',
      value: isOptimized && greenflowData
        ? `${greenflowData.fleet_utilisation_pct.toFixed(0)}%`
        : baselineData
        ? `${baselineData.fleet_utilisation_pct.toFixed(0)}%`
        : '--',
      icon: Activity,
      trend: isOptimized && benchmark && (greenflowData.fleet_utilisation_pct - baselineData.fleet_utilisation_pct) > 0
        ? `+${(greenflowData.fleet_utilisation_pct - baselineData.fleet_utilisation_pct).toFixed(0)}%`
        : null,
      trendPositive: true,
      subtitle: `${assignedCount} of ${totalRoutes} routes dispatched`,
      accent: 'blue',
    },
    {
      id: 'fuel-saved',
      label: isOptimized ? 'Total Fuel Saved' : 'Total Operating Cost',
      value: isOptimized && benchmark
        ? benchmark.fuel_saved_l.toFixed(1)
        : baselineData
        ? `$${baselineData.total_operating_cost.toFixed(0)}`
        : '--',
      unit: isOptimized ? 'L' : '',
      icon: TrendingDown,
      trend: isOptimized && benchmark ? `$${benchmark.cost_saved.toFixed(0)}` : null,
      trendPositive: true,
      subtitle: isOptimized && benchmark
        ? `Cost delta (-${benchmark.cost_saved_pct.toFixed(1)}%)`
        : 'Estimated uncoordinated cost',
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
