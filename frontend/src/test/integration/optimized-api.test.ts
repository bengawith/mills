import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { 
  getOeeData, 
  getUtilizationData, 
  getDowntimeAnalysisData,
  getRealTimeMetrics,
  getPerformanceSummary 
} from '../../lib/api'

// Create test server with MSW
const server = setupServer(
  // Mock optimized OEE endpoint
  http.get('*/api/v1/analytics/oee-optimized', () => {
    return HttpResponse.json({
      oee: 75.5,
      availability: 89.2,
      performance: 92.1,
      quality: 91.8,
      timestamp: '2025-08-26T10:00:00Z'
    })
  }),

  // Mock optimized utilization endpoint
  http.get('*/api/v1/analytics/utilization-optimized', () => {
    return HttpResponse.json({
      total_time_seconds: 86400,
      productive_uptime_seconds: 64800,
      unproductive_downtime_seconds: 21600,
      utilization_percentage: 75.0,
      timestamp: '2025-08-26T10:00:00Z'
    })
  }),

  // Mock optimized downtime analysis endpoint
  http.get('*/api/v1/analytics/downtime-analysis-optimized', () => {
    return HttpResponse.json({
      total_downtime_seconds: 21600,
      downtime_events: 8,
      average_downtime_duration: 2700,
      top_downtime_reasons: [
        { reason: 'Maintenance', duration_seconds: 10800, percentage: 50.0 },
        { reason: 'Setup', duration_seconds: 7200, percentage: 33.3 }
      ],
      timestamp: '2025-08-26T10:00:00Z'
    })
  }),

  // Mock real-time metrics endpoint
  http.get('*/api/v1/analytics/real-time-metrics', () => {
    return HttpResponse.json({
      active_machines: 12,
      total_machines: 15,
      fleet_utilization: 78.5,
      active_downtime_events: 3,
      timestamp: '2025-08-26T10:00:00Z'
    })
  }),

  // Mock performance summary endpoint
  http.get('*/api/v1/analytics/performance-summary', () => {
    return HttpResponse.json([
      {
        machine_id: 'machine_1',
        machine_name: 'Mill #1',
        utilization_percentage: 78.5,
        performance_score: 82.3,
        status: 'active'
      }
    ])
  })
)

// Enable request interception
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('API Integration Tests with Optimized Endpoints', () => {
  const mockParams = {
    start_time: '2025-08-20T00:00:00Z',
    end_time: '2025-08-26T23:59:59Z',
    machine_ids: ['machine_1', 'machine_2'],
    shift: 'DAY',
    day_of_week: 'MONDAY'
  }

  describe('Optimized Analytics Endpoints Integration', () => {
    it('successfully fetches OEE data from optimized endpoint', async () => {
      const response = await getOeeData(mockParams)
      
      expect(response.oee).toBe(75.5)
      expect(response.availability).toBe(89.2)
      expect(response.performance).toBe(92.1)
      expect(response.quality).toBe(91.8)
      expect(response.timestamp).toBe('2025-08-26T10:00:00Z')
    })

    it('successfully fetches utilization data from optimized endpoint', async () => {
      const response = await getUtilizationData(mockParams)
      
      expect(response.total_time_seconds).toBe(86400)
      expect(response.productive_uptime_seconds).toBe(64800)
      expect(response.unproductive_downtime_seconds).toBe(21600)
      expect(response.utilization_percentage).toBe(75.0)
      expect(response.timestamp).toBe('2025-08-26T10:00:00Z')
    })

    it('successfully fetches downtime analysis from optimized endpoint', async () => {
      const response = await getDowntimeAnalysisData(mockParams)
      
      expect(response.total_downtime_seconds).toBe(21600)
      expect(response.downtime_events).toBe(8)
      expect(response.average_downtime_duration).toBe(2700)
      expect(response.top_downtime_reasons).toHaveLength(2)
      expect(response.top_downtime_reasons[0].reason).toBe('Maintenance')
      expect(response.timestamp).toBe('2025-08-26T10:00:00Z')
    })

    it('successfully fetches real-time metrics', async () => {
      const response = await getRealTimeMetrics()
      
      expect(response.active_machines).toBe(12)
      expect(response.total_machines).toBe(15)
      expect(response.fleet_utilization).toBe(78.5)
      expect(response.active_downtime_events).toBe(3)
      expect(response.timestamp).toBe('2025-08-26T10:00:00Z')
    })

    it('successfully fetches performance summary', async () => {
      const response = await getPerformanceSummary(['machine_1'], 24)
      
      expect(Array.isArray(response)).toBe(true)
      expect(response).toHaveLength(1)
      expect(response[0].machine_id).toBe('machine_1')
      expect(response[0].machine_name).toBe('Mill #1')
      expect(response[0].utilization_percentage).toBe(78.5)
      expect(response[0].performance_score).toBe(82.3)
    })
  })

  describe('Performance Comparison Tests', () => {
    it('uses optimized endpoints instead of legacy ones', async () => {
      // Track which URLs are called
      const calledUrls: string[] = []
      
      server.use(
        http.get('*', ({ request }) => {
          calledUrls.push(request.url)
          return HttpResponse.json({})
        })
      )

      await getOeeData(mockParams)
      
      // Verify optimized endpoint is used
      expect(calledUrls.some(url => url.includes('oee-optimized'))).toBe(true)
      expect(calledUrls.some(url => url.includes('oee') && !url.includes('optimized'))).toBe(false)
    })

    it('handles concurrent requests efficiently', async () => {
      const startTime = Date.now()
      
      // Make concurrent requests
      const promises = [
        getOeeData(mockParams),
        getUtilizationData(mockParams),
        getDowntimeAnalysisData(mockParams),
        getRealTimeMetrics()
      ]
      
      const responses = await Promise.all(promises)
      const endTime = Date.now()
      
      // All requests should succeed
      expect(responses).toHaveLength(4)
      responses.forEach(response => {
        expect(response).toBeDefined()
      })
      
      // Should complete reasonably quickly (mock responses)
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('Error Handling Integration', () => {
    it('handles server errors gracefully', async () => {
      server.use(
        http.get('*/api/v1/analytics/oee-optimized', () => {
          return new HttpResponse(null, { status: 500 })
        })
      )

      await expect(getOeeData(mockParams)).rejects.toThrow()
    })

    it('handles network timeouts', async () => {
      server.use(
        http.get('*/api/v1/analytics/utilization-optimized', async () => {
          // Simulate timeout
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({})
        })
      )

      const response = await getUtilizationData(mockParams)
      expect(response).toBeDefined()
    })
  })
})
