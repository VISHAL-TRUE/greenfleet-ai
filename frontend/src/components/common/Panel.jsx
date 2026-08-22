import React from 'react'

export default function Panel({ title, icon: Icon, action, children, className = '' }) {
  return (
    <section className={`flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm ${className}`}>
      {title && (
        <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="h-4 w-4 text-emerald-400" />}
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              {title}
            </h2>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </section>
  )
}
