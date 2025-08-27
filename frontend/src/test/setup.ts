import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { beforeAll, afterEach, afterAll, vi } from 'vitest'
import { server } from './mocks/server'
import React from 'react'

// Mock WebSocket context BEFORE any imports
vi.mock('@/contexts/WebSocketContext', () => ({
  useWebSocket: () => ({
    connected: true,
    connecting: false,
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn(),
    subscribe: vi.fn(),
    unsubscribe: vi.fn(),
    subscriptions: [],
    on: vi.fn(),
    off: vi.fn(),
    ping: vi.fn(),
    getStatus: vi.fn()
  }),
  useDashboardEvents: () => ({
    lastUpdate: new Date('2025-08-27T09:00:00Z')
  }),
  useMaintenanceEvents: () => ({
    alerts: [],
    ticketUpdates: []
  }),
  useWebSocketEvent: vi.fn(),
  WebSocketProvider: ({ children }: { children: React.ReactNode }) => children,
}))

// Mock auth context
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 'test-user-1',
      email: 'test@example.com',
      username: 'testuser',
      full_name: 'Test User',
      role: 'operator',
      is_active: true
    },
    token: 'mock-jwt-token',
    isAuthenticated: true,
    login: vi.fn(),
    logout: vi.fn(),
    loading: false
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => children
}))

// Mock server setup
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
  
  // Mock localStorage with authentication token
  const localStorageMock = {
    getItem: (key: string) => {
      if (key === 'access_token') return 'mock-test-token'
      if (key === 'refresh_token') return 'mock-refresh-token'
      return null
    },
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
    length: 0,
    key: () => null
  }
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true
  })
})

afterEach(() => {
  cleanup()
  server.resetHandlers()
})

afterAll(() => server.close())

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  root = null
  rootMargin = ''
  thresholds = []
  
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() { return [] }
} as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
})

// Mock API functions
vi.mock('@/lib/api', () => ({
  // New optimized functions
  getQuickStats: vi.fn().mockResolvedValue({
    totalMachines: 5,
    activeMachines: 4,
    totalProduction: 1250,
    efficiency: 85.2,
    openTickets: 3,
    completedToday: 12,
  }),
  getMachineSummary: vi.fn().mockResolvedValue({
    machineData: [
      { id: '1', name: 'Mill 1', status: 'running', efficiency: 87.5 },
      { id: '2', name: 'Mill 2', status: 'idle', efficiency: 92.1 },
    ],
  }),
  getMaintenanceOverview: vi.fn().mockResolvedValue({
    upcomingMaintenance: 2,
    overdueMaintenance: 1,
    completedThisWeek: 8,
  }),
  getMachines: vi.fn().mockResolvedValue([
    { id: '1', name: 'Mill 1' },
    { id: '2', name: 'Mill 2' },
    { id: '3', name: 'Mill 3' },
  ]),
  getProductionData: vi.fn().mockResolvedValue([]),
  getMaintenanceData: vi.fn().mockResolvedValue([]),
  getInventoryData: vi.fn().mockResolvedValue([]),
  
  // Legacy API functions for backward compatibility
  getOeeData: vi.fn().mockResolvedValue({
    oee: 75.5,
    availability: 89.2,
    performance: 92.1,
    quality: 91.8,
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getUtilizationData: vi.fn().mockResolvedValue({
    total_time_seconds: 86400,
    productive_uptime_seconds: 64800,
    unproductive_downtime_seconds: 21600,
    utilization_percentage: 75.0,
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getDowntimeAnalysisData: vi.fn().mockResolvedValue({
    total_downtime_seconds: 21600,
    downtime_events: 8,
    average_downtime_duration: 2700,
    top_downtime_reasons: [
      { reason: 'Maintenance', duration_seconds: 10800, percentage: 50.0 },
      { reason: 'Setup', duration_seconds: 7200, percentage: 33.3 }
    ],
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getRealTimeMetrics: vi.fn().mockResolvedValue({
    active_machines: 12,
    total_machines: 15,
    fleet_utilization: 78.5,
    active_downtime_events: 3,
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getPerformanceSummary: vi.fn().mockResolvedValue([
    {
      machine_id: 'machine_1',
      machine_name: 'Mill #1',
      utilization_percentage: 78.5,
      performance_score: 82.3,
      summary: 'Performance data',
      timestamp: '2025-08-26T10:00:00Z'
    }
  ]),
  getTrendsData: vi.fn().mockResolvedValue({
    trends: [],
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getMachineComparison: vi.fn().mockResolvedValue({
    machines: [
      {
        machine_id: 'machine_1',
        metric_value: 85.5
      },
      {
        machine_id: 'machine_2', 
        metric_value: 78.2
      }
    ],
    comparison: {},
    timestamp: '2025-08-26T10:00:00Z'
  }),
  getEfficiencyInsights: vi.fn().mockResolvedValue({
    machine_insights: [
      {
        machine_id: 'machine_1',
        efficiency_score: 87.5,
        insights: ['High performance', 'Low downtime']
      }
    ],
    fleet_insights: [
      {
        category: 'Overall Fleet',
        score: 85.2,
        recommendations: ['Optimize maintenance schedule']
      }
    ],
    summary: {
      period_hours: 168,
      machines_analyzed: 1
    },
    insights: [],
    timestamp: '2025-08-26T10:00:00Z'
  }),
}));
