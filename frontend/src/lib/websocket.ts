/**
 * WebSocket client for real-time updates in Mill Dash.
 * Provides connection management and event handling for live dashboard updates.
 */

import { EventTypes } from './websocket-types';

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp: string;
}

export interface ConnectionStats {
  total_connections: number;
  subscriptions: Record<string, number>;
  clients: Array<{
    client_id: string;
    connected_at: string;
    subscriptions: string[];
  }>;
}

export type EventHandler = (data: any) => void;
export type ConnectionStatusHandler = (connected: boolean) => void;

export class MillDashWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private clientId: string;
  private eventHandlers: Map<string, EventHandler[]> = new Map();
  private connectionHandlers: ConnectionStatusHandler[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private isConnected = false;
  private subscriptions: Set<string> = new Set();
  
  constructor(baseUrl: string = 'ws://localhost:8000', clientId: string = 'frontend') {
    this.url = `${baseUrl}/api/v1/ws?client_id=${clientId}`;
    this.clientId = clientId;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected to Mill Dash');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.notifyConnectionHandlers(true);
          
          // Resubscribe to previous subscriptions
          if (this.subscriptions.size > 0) {
            this.subscribe(Array.from(this.subscriptions));
          }
          
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        this.ws.onclose = (event) => {
          console.log(`🔌 WebSocket disconnected: ${event.code} ${event.reason}`);
          this.isConnected = false;
          this.notifyConnectionHandlers(false);
          
          // Attempt to reconnect unless it was a clean close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Subscribe to specific event types
   */
  subscribe(eventTypes: string[]): void {
    if (!this.isConnected || !this.ws) {
      // Store subscriptions for when we connect
      eventTypes.forEach(type => this.subscriptions.add(type));
      return;
    }

    const message = {
      type: 'subscribe',
      subscriptions: eventTypes
    };

    this.ws.send(JSON.stringify(message));
    eventTypes.forEach(type => this.subscriptions.add(type));
  }

  /**
   * Unsubscribe from specific event types
   */
  unsubscribe(eventTypes: string[]): void {
    if (!this.isConnected || !this.ws) {
      eventTypes.forEach(type => this.subscriptions.delete(type));
      return;
    }

    const message = {
      type: 'unsubscribe',
      subscriptions: eventTypes
    };

    this.ws.send(JSON.stringify(message));
    eventTypes.forEach(type => this.subscriptions.delete(type));
  }

  /**
   * Add event handler for specific event type
   */
  on(eventType: string, handler: EventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  /**
   * Remove event handler
   */
  off(eventType: string, handler: EventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Add connection status handler
   */
  onConnectionChange(handler: ConnectionStatusHandler): void {
    this.connectionHandlers.push(handler);
  }

  /**
   * Send ping to test connection
   */
  ping(): void {
    if (this.isConnected && this.ws) {
      const message = {
        type: 'ping',
        timestamp: new Date().toISOString()
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Get connection status
   */
  getStatus(): void {
    if (this.isConnected && this.ws) {
      const message = { type: 'get_status' };
      this.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Check if currently connected
   */
  get connected(): boolean {
    return this.isConnected;
  }

  /**
   * Get current subscriptions
   */
  get currentSubscriptions(): string[] {
    return Array.from(this.subscriptions);
  }

  private handleMessage(message: WebSocketMessage): void {
    const { type, data } = message;
    
    // Handle system messages
    switch (type) {
      case 'connection_established':
        console.log('✅ WebSocket connection established');
        break;
        
      case 'subscription_confirmed':
        console.log('📋 Subscriptions confirmed:', data?.subscriptions);
        break;
        
      case 'pong':
        console.log('🏓 Pong received');
        break;
        
      case 'status_response':
        console.log('📊 Connection status:', data);
        break;
        
      case 'error':
        console.error('❌ WebSocket error:', data?.message);
        break;
        
      default:
        // Handle custom events
        this.notifyEventHandlers(type, data);
        break;
    }
  }

  private notifyEventHandlers(eventType: string, data: any): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${eventType}:`, error);
        }
      });
    }
  }

  private notifyConnectionHandlers(connected: boolean): void {
    this.connectionHandlers.forEach(handler => {
      try {
        handler(connected);
      } catch (error) {
        console.error('Error in connection handler:', error);
      }
    });
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${this.reconnectDelay}ms`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
      });
    }, this.reconnectDelay);
  }
}

// Create and export a singleton instance
export const webSocketClient = new MillDashWebSocket(
  import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000',
  'mill-dash-frontend'
);
