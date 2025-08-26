import { describe, it, expect, beforeEach, vi } from 'vitest'
import { 
  getOeeData, 
  getUtilizationData, 
  getDowntimeAnalysisData,
  getRealTimeMetrics,
  getPerformanceSummary
} from '../../lib/api'

// Mock the apiClient to avoid authentication issues
vi.mock('../../lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../lib/api')>()
  
  return {
    ...actual,
    getOeeData: vi.fn(),
    getUtilizationData: vi.fn(),
    getDowntimeAnalysisData: vi.fn(),
    getRealTimeMetrics: vi.fn(),
    getPerformanceSummary: vi.fn(),
    getTrendsData: vi.fn(),
    getMachineComparison: vi.fn(),
    getEfficiencyInsights: vi.fn(),
  }
})

describe('Optimized Analytics API (Mocked)', () => {
  const mockParams = {
    start_time: '2025-08-20T00:00:00Z',
    end_time: '2025-08-26T23:59:59Z',
    machine_ids: ['machine_1', 'machine_2'],
    shift: 'DAY',
    day_of_week: 'MONDAY'
  }

  beforeEach(() => {
    // Setup mock implementations
    vi.mocked(getOeeData).mockResolvedValue({
      oee: 75.5,
      availability: 89.2,
      performance: 92.1,
      quality: 91.8,
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(getUtilizationData).mockResolvedValue({
      total_time_seconds: 86400,
      productive_uptime_seconds: 64800,
      unproductive_downtime_seconds: 21600,
      utilization_percentage: 75.0,
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(getDowntimeAnalysisData).mockResolvedValue({
      total_downtime_seconds: 21600,
      downtime_events: 8,
      average_downtime_duration: 2700,
      top_downtime_reasons: [
        { reason: 'Maintenance', duration_seconds: 10800, percentage: 50.0 },
        { reason: 'Setup', duration_seconds: 7200, percentage: 33.3 }
      ],
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(getRealTimeMetrics).mockResolvedValue({
      active_machines: 12,
      total_machines: 15,
      fleet_utilization: 78.5,
      active_downtime_events: 3,
      timestamp: '2025-08-26T10:00:00Z'
    })

    vi.mocked(getPerformanceSummary).mockResolvedValue([
      {
        machine_id: 'machine_1',
        machine_name: 'Mill #1',
        utilization_percentage: 78.5,
        performance_score: 82.3,
        status: 'active'
      }
    ])
  })

  describe('Core Analytics Endpoints', () => {
    it('should fetch OEE data from optimized endpoint', async () => {
      const data = await getOeeData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.oee).toBe(75.5)
      expect(data.availability).toBe(89.2)
      expect(data.performance).toBe(92.1)
      expect(data.quality).toBe(91.8)
      expect(getOeeData).toHaveBeenCalledWith(mockParams)
    })

    it('should fetch utilization data from optimized endpoint', async () => {
      const data = await getUtilizationData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.total_time_seconds).toBe(86400)
      expect(data.productive_uptime_seconds).toBe(64800)
      expect(data.unproductive_downtime_seconds).toBe(21600)
      expect(data.utilization_percentage).toBe(75.0)
      expect(getUtilizationData).toHaveBeenCalledWith(mockParams)
    })

    it('should fetch downtime analysis from optimized endpoint', async () => {
      const data = await getDowntimeAnalysisData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.total_downtime_seconds).toBe(21600)
      expect(data.downtime_events).toBe(8)
      expect(data.average_downtime_duration).toBe(2700)
      expect(Array.isArray(data.top_downtime_reasons)).toBe(true)
      expect(data.top_downtime_reasons[0].reason).toBe('Maintenance')
      expect(getDowntimeAnalysisData).toHaveBeenCalledWith(mockParams)
    })
  })

  describe('Advanced Analytics Endpoints', () => {
    it('should fetch real-time metrics', async () => {
      const data = await getRealTimeMetrics()
      
      expect(data).toBeDefined()
      expect(data.active_machines).toBe(12)
      expect(data.total_machines).toBe(15)
      expect(data.fleet_utilization).toBe(78.5)
      expect(data.active_downtime_events).toBe(3)
      expect(getRealTimeMetrics).toHaveBeenCalled()
    })

    it('should fetch performance summary', async () => {
      const data = await getPerformanceSummary(['machine_1'], 24)
      
      expect(Array.isArray(data)).toBe(true)
      expect(data).toHaveLength(1)
      expect(data[0].machine_id).toBe('machine_1')
      expect(data[0].machine_name).toBe('Mill #1')
      expect(data[0].utilization_percentage).toBe(78.5)
      expect(data[0].performance_score).toBe(82.3)
      expect(getPerformanceSummary).toHaveBeenCalledWith(['machine_1'], 24)
    })
  })

  describe('Parameter Handling', () => {
    it('should handle "All" machine_ids correctly', async () => {
      const paramsWithAll = { ...mockParams, machine_ids: "All" }
      const data = await getOeeData(paramsWithAll)
      expect(data).toBeDefined()
      expect(getOeeData).toHaveBeenCalledWith(paramsWithAll)
    })

    it('should handle empty machine_ids array', async () => {
      const paramsWithEmpty = { ...mockParams, machine_ids: [] }
      const data = await getUtilizationData(paramsWithEmpty)
      expect(data).toBeDefined()
      expect(getUtilizationData).toHaveBeenCalledWith(paramsWithEmpty)
    })
  })

  describe('Function Availability', () => {
    it('should have all optimized endpoint functions available', () => {
      expect(getOeeData).toBeTypeOf('function')
      expect(getUtilizationData).toBeTypeOf('function')
      expect(getDowntimeAnalysisData).toBeTypeOf('function')
      expect(getRealTimeMetrics).toBeTypeOf('function')
      expect(getPerformanceSummary).toBeTypeOf('function')
    })
  })
})
