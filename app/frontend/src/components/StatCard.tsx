import React from 'react'
import { Card, CardContent, Box, Typography } from '@mui/material'
import { TrendingUp, TrendingDown } from '@mui/icons-material'

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  bgColor?: string
  isScore?: boolean
  trend?: number
}

export default function StatCard({ 
  title, 
  value, 
  icon, 
  bgColor = 'primary',
  isScore,
  trend 
}: StatCardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: '0 12px 24px rgba(0, 0, 0, 0.12)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>
            {title}
          </Typography>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 1.5,
              bgcolor: `${bgColor}.lighter` || 'primary.lighter',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: `${bgColor}.main` || 'primary.main',
            }}
          >
            {icon}
          </Box>
        </Box>

        <Box sx={{ mb: 1 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 0.5 }}>
            {value}
            {isScore && <Typography component="span" variant="body2" color="textSecondary">/10</Typography>}
          </Typography>
        </Box>

        {trend !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {trend > 0 ? <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} /> : <TrendingDown sx={{ fontSize: 16, color: 'error.main' }} />}
            <Typography variant="caption" color={trend > 0 ? 'success.main' : 'error.main'} sx={{ fontWeight: 500 }}>
              {trend > 0 ? '+' : ''}{trend}% vs last month
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}
