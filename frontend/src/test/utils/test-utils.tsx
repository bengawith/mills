import React, { createContext, useContext } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'

// Mock the auth context
const mockAuthContext = {
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
}

// Mock WebSocket context
const mockWebSocketContext = {
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
}

// Create the WebSocket context for tests
const WebSocketContext = createContext(mockWebSocketContext)

// Create mock auth provider
const MockAuthProvider = ({ children }: { children: React.ReactNode }) => {
  return <div data-testid="auth-provider">{children}</div>
}

// Create mock WebSocket provider
const MockWebSocketProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <WebSocketContext.Provider value={mockWebSocketContext}>
      {children}
    </WebSocketContext.Provider>
  )
}

// Create a test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MockAuthProvider>
          <MockWebSocketProvider>
            {children}
          </MockWebSocketProvider>
        </MockAuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

// Custom render function
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: TestWrapper, ...options })

// Export everything
export * from '@testing-library/react'
export { customRender as render, TestWrapper, mockAuthContext, mockWebSocketContext }
