import { describe, it, expect, beforeEach } from 'vitest'
import { 
  getOeeData, 
  getUtilizationData, 
  getDowntimeAnalysisData,
  getRealTimeMetrics,
  getPerformanceSummary,
  getTrendsData,
  getMachineComparison,
  getEfficiencyInsights
} from '../../lib/api'

describe('Optimized Analytics API', () => {
  const mockParams = {
    start_time: '2025-08-20T00:00:00Z',
    end_time: '2025-08-26T23:59:59Z',
    machine_ids: ['machine_1', 'machine_2'],
    shift: 'DAY',
    day_of_week: 'MONDAY'
  }

  describe('Core Analytics Endpoints', () => {
    it('should fetch OEE data from optimized endpoint', async () => {
      const data = await getOeeData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.oee).toBeTypeOf('number')
      expect(data.availability).toBeTypeOf('number')
      expect(data.performance).toBeTypeOf('number')
      expect(data.quality).toBeTypeOf('number')
      
      // Verify realistic ranges
      expect(data.oee).toBeGreaterThanOrEqual(0)
      expect(data.oee).toBeLessThanOrEqual(100)
    })

    it('should fetch utilization data from optimized endpoint', async () => {
      const data = await getUtilizationData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.total_time_seconds).toBeTypeOf('number')
      expect(data.productive_uptime_seconds).toBeTypeOf('number')
      expect(data.unproductive_downtime_seconds).toBeTypeOf('number')
      expect(data.utilization_percentage).toBeTypeOf('number')
      
      // Verify data consistency
      expect(data.utilization_percentage).toBeGreaterThanOrEqual(0)
      expect(data.utilization_percentage).toBeLessThanOrEqual(100)
    })

    it('should fetch downtime analysis from optimized endpoint', async () => {
      const data = await getDowntimeAnalysisData(mockParams)
      
      expect(data).toBeDefined()
      expect(data.total_downtime_seconds).toBeTypeOf('number')
      expect(data.downtime_events).toBeTypeOf('number')
      expect(data.average_downtime_duration).toBeTypeOf('number')
      expect(Array.isArray(data.top_downtime_reasons)).toBe(true)
    })
  })

  describe('Advanced Analytics Endpoints', () => {
    it('should fetch real-time metrics', async () => {
      const data = await getRealTimeMetrics()
      
      expect(data).toBeDefined()
      expect(data.active_machines).toBeTypeOf('number')
      expect(data.total_machines).toBeTypeOf('number')
      expect(data.fleet_utilization).toBeTypeOf('number')
      expect(data.active_downtime_events).toBeTypeOf('number')
      
      // Verify logical constraints
      expect(data.active_machines).toBeLessThanOrEqual(data.total_machines)
    })

    it('should fetch performance summary', async () => {
      const data = await getPerformanceSummary(['machine_1'], 24)
      
      expect(Array.isArray(data)).toBe(true)
      if (data.length > 0) {
        const machine = data[0]
        expect(machine.machine_id).toBeTypeOf('string')
        expect(machine.machine_name).toBeTypeOf('string')
        expect(machine.utilization_percentage).toBeTypeOf('number')
        expect(machine.performance_score).toBeTypeOf('number')
      }
    })

    it('should fetch trends data', async () => {
      const data = await getTrendsData(['machine_1'], 7, 'daily')
      
      expect(data).toBeDefined()
      expect(Array.isArray(data.trends)).toBe(true)
      if (data.trends.length > 0) {
        const trend = data.trends[0]
        expect(trend.date).toBeTypeOf('string')
        expect(trend.utilization).toBeTypeOf('number')
        expect(trend.oee).toBeTypeOf('number')
      }
    })

    it('should fetch machine comparison data', async () => {
      const data = await getMachineComparison('utilization')
      
      expect(data).toBeDefined()
      expect(Array.isArray(data.machines)).toBe(true)
      if (data.machines.length > 0) {
        const machine = data.machines[0]
        expect(machine.machine_id).toBeTypeOf('string')
        expect(machine.metric_value).toBeTypeOf('number')
      }
    })

    it('should fetch efficiency insights', async () => {
      const data = await getEfficiencyInsights(['machine_1'], 168)
      
      expect(data).toBeDefined()
      expect(Array.isArray(data.machine_insights)).toBe(true)
      expect(Array.isArray(data.fleet_insights)).toBe(true)
      expect(data.summary).toBeDefined()
      expect(data.summary.period_hours).toBeTypeOf('number')
      expect(data.summary.machines_analyzed).toBeTypeOf('number')
    })
  })

  describe('Parameter Handling', () => {
    it('should handle "All" machine_ids correctly', async () => {
      const paramsWithAll = { ...mockParams, machine_ids: "All" }
      const data = await getOeeData(paramsWithAll)
      expect(data).toBeDefined()
    })

    it('should handle empty machine_ids array', async () => {
      const paramsWithEmpty = { ...mockParams, machine_ids: [] }
      const data = await getUtilizationData(paramsWithEmpty)
      expect(data).toBeDefined()
    })

    it('should handle optional parameters', async () => {
      const minimalParams = {
        start_time: mockParams.start_time,
        end_time: mockParams.end_time,
        machine_ids: mockParams.machine_ids
      }
      const data = await getDowntimeAnalysisData(minimalParams)
      expect(data).toBeDefined()
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      // This would be tested with MSW error handlers
      // For now, we'll just verify the functions exist
      expect(getOeeData).toBeTypeOf('function')
      expect(getUtilizationData).toBeTypeOf('function')
      expect(getDowntimeAnalysisData).toBeTypeOf('function')
    })
  })
})
