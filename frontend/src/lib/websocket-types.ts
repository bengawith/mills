/**
 * WebSocket event types and interfaces for Mill Dash real-time communication.
 */

export const EventTypes = {
  // Machine events
  MACHINE_STATUS_UPDATE: 'machine_status_update',
  
  // Maintenance events  
  MAINTENANCE_ALERT: 'maintenance_alert',
  TICKET_STATUS_CHANGE: 'ticket_status_change',
  TICKET_CREATED: 'ticket_created',
  
  // Production events
  PRODUCTION_METRIC_UPDATE: 'production_metric_update',
  
  // Dashboard events
  DASHBOARD_REFRESH: 'dashboard_refresh',
  
  // System events
  SYSTEM_ALERT: 'system_alert',
  HEARTBEAT: 'heartbeat',
  
  // Connection events
  CONNECTION_ESTABLISHED: 'connection_established',
  SUBSCRIPTION_CONFIRMED: 'subscription_confirmed',
  UNSUBSCRIPTION_CONFIRMED: 'unsubscription_confirmed',
  ERROR: 'error',
  PING: 'ping',
  PONG: 'pong'
} as const;

export type EventType = typeof EventTypes[keyof typeof EventTypes];

// Event data interfaces
export interface MachineStatusUpdate {
  machine_id: string;
  status: string;
  utilization?: number;
  timestamp: string;
}

export interface MaintenanceAlert {
  ticket_id: number;
  machine_id: string;
  priority: string;
  description: string;
  timestamp: string;
}

export interface TicketStatusChange {
  ticket_id: number;
  old_status: string;
  new_status: string;
  machine_id: string;
  timestamp: string;
}

export interface ProductionMetricUpdate {
  metrics: Record<string, any>;
  timestamp: string;
}

export interface DashboardRefresh {
  refresh_all: boolean;
  timestamp: string;
}

export interface SystemAlert {
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: string;
}

// Subscription types
export const SubscriptionTypes = {
  ALL: 'all',
  DASHBOARD: 'dashboard', 
  MAINTENANCE: 'maintenance',
  MACHINES: 'machines',
  PRODUCTION: 'production'
} as const;

export type SubscriptionType = typeof SubscriptionTypes[keyof typeof SubscriptionTypes];

// WebSocket message structure
export interface WebSocketEvent {
  type: EventType;
  data: any;
  timestamp: string;
}

// Connection status
export interface ConnectionStatus {
  connected: boolean;
  reconnecting: boolean;
  subscriptions: SubscriptionType[];
  lastActivity: string;
}
