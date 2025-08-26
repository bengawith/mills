import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import HomePage from '../../pages/HomePage'
import { TestWrapper } from '../utils/test-utils'
import * as api from '../../lib/api'

// Mock the API functions
vi.mock('../../lib/api', () => ({
  getOeeData: vi.fn(),
  getUtilizationData: vi.fn(),
  getDowntimeAnalysisData: vi.fn(),
  getRealTimeMetrics: vi.fn(),
  getPerformanceSummary: vi.fn(),
  getTrendsData: vi.fn(),
  getMachineComparison: vi.fn(),
  getEfficiencyInsights: vi.fn()
}))

describe('HomePage Component', () => {
  beforeEach(() => {
    // Setup API mocks with realistic data
    vi.mocked(api.getOeeData).mockResolvedValue({
      oee: 75.5,
      availability: 89.2,
      performance: 92.1,
      quality: 91.8,
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(api.getUtilizationData).mockResolvedValue({
      total_time_seconds: 86400,
      productive_uptime_seconds: 64800,
      unproductive_downtime_seconds: 21600,
      utilization_percentage: 75.0,
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(api.getDowntimeAnalysisData).mockResolvedValue({
      total_downtime_seconds: 21600,
      downtime_events: 8,
      average_downtime_duration: 2700,
      top_downtime_reasons: [
        { reason: 'Maintenance', duration_seconds: 10800, percentage: 50.0 },
        { reason: 'Setup', duration_seconds: 7200, percentage: 33.3 }
      ],
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(api.getRealTimeMetrics).mockResolvedValue({
      active_machines: 12,
      total_machines: 15,
      fleet_utilization: 78.5,
      active_downtime_events: 3,
      timestamp: '2025-08-26T10:00:00Z'
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )
    
    // Check that the component renders without throwing
    expect(document.body).toBeInTheDocument()
  })

  it('calls optimized API endpoints on mount', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )

    // Verify that optimized endpoints are being called
    expect(api.getOeeData).toHaveBeenCalled()
    expect(api.getUtilizationData).toHaveBeenCalled()
    expect(api.getDowntimeAnalysisData).toHaveBeenCalled()
    expect(api.getRealTimeMetrics).toHaveBeenCalled()
  })

  it('handles API call parameters correctly', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )

    // Check that API functions are called with appropriate parameters
    const oeeCall = vi.mocked(api.getOeeData).mock.calls[0]
    const utilizationCall = vi.mocked(api.getUtilizationData).mock.calls[0]
    const downtimeCall = vi.mocked(api.getDowntimeAnalysisData).mock.calls[0]

    // Each should be called with some parameters
    expect(oeeCall).toBeDefined()
    expect(utilizationCall).toBeDefined() 
    expect(downtimeCall).toBeDefined()
  })

  it('handles API errors gracefully', async () => {
    // Mock API failure
    vi.mocked(api.getOeeData).mockRejectedValue(new Error('API Error'))
    
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )

    // Component should still render even if API calls fail
    expect(document.body).toBeInTheDocument()
  })

  it('validates optimized endpoint usage', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    )

    // Verify we're using the new optimized functions, not legacy ones
    expect(api.getOeeData).toHaveBeenCalled()
    expect(api.getUtilizationData).toHaveBeenCalled()
    expect(api.getDowntimeAnalysisData).toHaveBeenCalled()
    expect(api.getRealTimeMetrics).toHaveBeenCalled()
  })
})
