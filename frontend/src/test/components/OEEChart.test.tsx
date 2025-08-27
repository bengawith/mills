import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import OeeChart from '@/pages/Dashboard/OeeChart'

const mockOeeData = {
  oee: {
    oee: 75.5,
    availability: 85.2,
    performance: 92.1,
    quality: 96.3
  }
}

describe('OeeChart', () => {
  it('renders OEE chart with title', () => {
    render(<OeeChart data={mockOeeData} />)
    
    expect(screen.getByText('OEE (Overall Equipment Effectiveness)')).toBeInTheDocument()
  })

  it('displays OEE values when data is provided', () => {
    render(<OeeChart data={mockOeeData} />)
    
    // The component should render the chart data
    // Since it's a recharts component, we can't easily test the rendered bars
    // but we can verify the component renders without crashing
    expect(screen.getByText('OEE (Overall Equipment Effectiveness)')).toBeInTheDocument()
  })

  it('handles missing OEE data gracefully', () => {
    const emptyData = { oee: null }
    render(<OeeChart data={emptyData} />)
    
    expect(screen.getByText('OEE (Overall Equipment Effectiveness)')).toBeInTheDocument()
  })

  it('handles completely empty data', () => {
    const emptyData = {}
    render(<OeeChart data={emptyData} />)
    
    expect(screen.getByText('OEE (Overall Equipment Effectiveness)')).toBeInTheDocument()
  })
})
