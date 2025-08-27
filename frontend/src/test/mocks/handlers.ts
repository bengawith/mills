import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8000/api/v1'

// Mock data
const mockOeeData = {
  oee: 75.5,
  availability: 85.2,
  performance: 92.1,
  quality: 96.3
}

const mockUtilizationData = {
  total_time_seconds: 86400,
  productive_uptime_seconds: 65000,
  unproductive_downtime_seconds: 15000,
  productive_downtime_seconds: 6400,
  utilization_percentage: 75.23
}

const mockDowntimeData = {
  total_downtime_seconds: 15000,
  downtime_events: 8,
  average_downtime_duration: 1875,
  excessive_downtime_events: 2,
  top_downtime_reasons: [
    { reason: 'Maintenance', duration_seconds: 7200, count: 3 },
    { reason: 'Setup', duration_seconds: 4800, count: 2 }
  ]
}

const mockRealTimeMetrics = {
  active_machines: 12,
  total_machines: 15,
  fleet_utilization: 78.5,
  active_downtime_events: 3,
  current_production_runs: 8,
  pending_maintenance_tickets: 5
}

const mockPerformanceSummary = [
  {
    machine_id: 'machine_1',
    machine_name: 'Mill 1',
    utilization_percentage: 78.5,
    downtime_events: 4,
    total_runtime_hours: 22.5,
    performance_score: 85.2
  }
]

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/users/`, () => {
    return HttpResponse.json({ 
      user_id: 1, 
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'EMPLOYEE',
      onboarded: true
    })
  }),

  http.post(`${API_BASE}/auth/token`, () => {
    return HttpResponse.json({
      access_token: 'mock-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer'
    })
  }),

  // Handle OPTIONS requests for CORS preflight
  http.options('*', () => {
    return new HttpResponse(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }
    })
  }),

  // Optimized Analytics endpoints with proper parameter handling
  http.get(`${API_BASE}/analytics/oee-optimized`, ({ request }) => {
    const url = new URL(request.url)
    const startTime = url.searchParams.get('start_time')
    const endTime = url.searchParams.get('end_time')
    
    // Mock response with request parameters included for verification
    return HttpResponse.json({
      ...mockOeeData,
      request_params: {
        start_time: startTime,
        end_time: endTime,
        machine_ids: url.searchParams.getAll('machine_ids[]'),
        shift: url.searchParams.get('shift'),
        day_of_week: url.searchParams.get('day_of_week')
      }
    })
  }),

  http.get(`${API_BASE}/analytics/utilization-optimized`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json({
      ...mockUtilizationData,
      request_params: {
        start_time: url.searchParams.get('start_time'),
        end_time: url.searchParams.get('end_time'),
        machine_ids: url.searchParams.getAll('machine_ids[]'),
        shift: url.searchParams.get('shift'),
        day_of_week: url.searchParams.get('day_of_week')
      }
    })
  }),

  http.get(`${API_BASE}/analytics/downtime-analysis-optimized`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json({
      ...mockDowntimeData,
      request_params: {
        start_time: url.searchParams.get('start_time'),
        end_time: url.searchParams.get('end_time'),
        machine_ids: url.searchParams.getAll('machine_ids[]'),
        shift: url.searchParams.get('shift'),
        day_of_week: url.searchParams.get('day_of_week')
      }
    })
  }),

  http.get(`${API_BASE}/analytics/real-time-metrics`, () => {
    return HttpResponse.json(mockRealTimeMetrics)
  }),

  http.get(`${API_BASE}/analytics/performance-summary`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json(mockPerformanceSummary)
  }),

  http.get(`${API_BASE}/analytics/trends`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json({
      trends: [
        { date: '2025-08-20', utilization: 75.2, oee: 72.1 },
        { date: '2025-08-21', utilization: 78.5, oee: 75.8 },
        { date: '2025-08-22', utilization: 82.1, oee: 78.9 }
      ],
      request_params: {
        days_back: url.searchParams.get('days_back'),
        interval: url.searchParams.get('interval'),
        machine_ids: url.searchParams.getAll('machine_ids[]')
      }
    })
  }),

  http.get(`${API_BASE}/analytics/machine-comparison`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json({
      machines: [
        { machine_id: 'machine_1', metric_value: 78.5 },
        { machine_id: 'machine_2', metric_value: 82.1 }
      ],
      request_params: {
        metric: url.searchParams.get('metric'),
        start_time: url.searchParams.get('start_time'),
        end_time: url.searchParams.get('end_time')
      }
    })
  }),

  http.get(`${API_BASE}/analytics/efficiency-insights`, ({ request }) => {
    const url = new URL(request.url)
    return HttpResponse.json({
      machine_insights: [],
      fleet_insights: [],
      summary: {
        period_hours: parseInt(url.searchParams.get('hours_back') || '168'),
        machines_analyzed: 2,
        avg_performance_score: 80.3
      },
      request_params: {
        hours_back: url.searchParams.get('hours_back'),
        machine_ids: url.searchParams.getAll('machine_ids[]')
      }
    })
  }),

  // Dashboard endpoints
  http.get(`${API_BASE}/dashboard/quick-stats`, () => {
    return HttpResponse.json({
      active_machines: 12,
      total_downtime_minutes: 450,
      production_efficiency: 85.2,
      pending_tickets: 5
    })
  }),

  http.get(`${API_BASE}/dashboard/machine-summary`, () => {
    return HttpResponse.json([
      {
        machine_id: 'machine_1',
        status: 'RUNNING',
        current_utilization: 78.5,
        last_maintenance: '2025-08-20T10:00:00Z'
      }
    ])
  }),

  http.get(`${API_BASE}/dashboard/analytical-data-optimized`, () => {
    return HttpResponse.json({
      machines: mockPerformanceSummary,
      summary: mockRealTimeMetrics
    })
  }),

  // Maintenance endpoints
  http.get(`${API_BASE}/dashboard/maintenance-overview`, () => {
    return HttpResponse.json({
      open_tickets: 5,
      overdue_tickets: 2,
      completed_this_week: 12,
      avg_resolution_hours: 8.5
    })
  }),
]
