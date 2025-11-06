import React from 'react'

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  bgColor: string
  isScore?: boolean
}

export default function StatCard({ title, value, icon, bgColor, isScore }: StatCardProps) {
  return (
    <div className={`${bgColor} p-6 rounded-xl border border-cream-200 shadow-sm hover:shadow-md transition`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 text-xs font-medium uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-serif font-bold text-primary mt-2">
            {isScore ? value : value}
            {isScore && <span className="text-lg">/10</span>}
          </p>
        </div>
        <div className="p-3 rounded-lg bg-white/50">
          {icon}
        </div>
      </div>
    </div>
  )
}
