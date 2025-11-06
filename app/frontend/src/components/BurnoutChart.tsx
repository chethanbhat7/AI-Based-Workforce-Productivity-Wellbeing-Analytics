import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function BurnoutChart() {
  const data = [
    { name: 'Week 1', high: 40, medium: 120, low: 1090 },
    { name: 'Week 2', high: 35, medium: 115, low: 1100 },
    { name: 'Week 3', high: 38, medium: 125, low: 1087 },
    { name: 'Week 4', high: 45, medium: 120, low: 1085 },
  ]

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Burnout Risk Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="high" stackId="a" fill="#ef4444" />
          <Bar dataKey="medium" stackId="a" fill="#eab308" />
          <Bar dataKey="low" stackId="a" fill="#22c55e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
