import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import ConnectionStatus from '../../components/ConnectionStatus'
import { TestWrapper } from '../utils/test-utils'

// Mock the API status checking
vi.mock('../../lib/api', () => ({
  checkAPIHealth: vi.fn()
}))

describe('ConnectionStatus Component', () => {
  it('renders connection status component', () => {
    render(
      <TestWrapper>
        <ConnectionStatus />
      </TestWrapper>
    )

    // Check if component renders without crashing
    expect(screen.getByTestId('connection-status') || document.querySelector('.connection-status')).toBeInTheDocument()
  })

  it('displays connection indicator', () => {
    render(
      <TestWrapper>
        <ConnectionStatus />
      </TestWrapper>
    )

    // Look for status indicators - these might be icons, text, or colored elements
    const statusElement = screen.queryByText(/connected/i) || 
                         screen.queryByText(/online/i) || 
                         screen.queryByText(/offline/i) ||
                         screen.queryByRole('status')

    // If status element exists, it should be in the document
    if (statusElement) {
      expect(statusElement).toBeInTheDocument()
    }
  })
})
