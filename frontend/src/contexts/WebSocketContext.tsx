/**
 * React context for WebSocket real-time communication.
 * Provides WebSocket connection management and event handling throughout the app.
 */

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { webSocketClient, MillDashWebSocket } from '@/lib/websocket';
import { EventTypes, SubscriptionTypes, type EventType, type SubscriptionType } from '@/lib/websocket-types';

interface WebSocketContextType {
  // Connection state
  connected: boolean;
  connecting: boolean;
  
  // Connection management
  connect: () => Promise<void>;
  disconnect: () => void;
  
  // Subscription management
  subscribe: (eventTypes: SubscriptionType[]) => void;
  unsubscribe: (eventTypes: SubscriptionType[]) => void;
  subscriptions: SubscriptionType[];
  
  // Event handling
  on: (eventType: EventType, handler: (data: any) => void) => void;
  off: (eventType: EventType, handler: (data: any) => void) => void;
  
  // Utility functions
  ping: () => void;
  getStatus: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
  autoSubscriptions?: SubscriptionType[];
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  children, 
  autoConnect = true,
  autoSubscriptions = [SubscriptionTypes.ALL]
}) => {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [subscriptions, setSubscriptions] = useState<SubscriptionType[]>([]);

  // Connection management
  const connect = useCallback(async () => {
    if (connected || connecting) return;
    
    setConnecting(true);
    try {
      await webSocketClient.connect();
      setConnected(true);
      
      // Auto-subscribe if specified
      if (autoSubscriptions.length > 0) {
        subscribe(autoSubscriptions);
      }
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    } finally {
      setConnecting(false);
    }
  }, [connected, connecting, autoSubscriptions]);

  const disconnect = useCallback(() => {
    webSocketClient.disconnect();
    setConnected(false);
    setSubscriptions([]);
  }, []);

  // Subscription management
  const subscribe = useCallback((eventTypes: SubscriptionType[]) => {
    webSocketClient.subscribe(eventTypes);
    setSubscriptions(prev => {
      const newSubs = new Set([...prev, ...eventTypes]);
      return Array.from(newSubs);
    });
  }, []);

  const unsubscribe = useCallback((eventTypes: SubscriptionType[]) => {
    webSocketClient.unsubscribe(eventTypes);
    setSubscriptions(prev => prev.filter(sub => !eventTypes.includes(sub)));
  }, []);

  // Event handling
  const on = useCallback((eventType: EventType, handler: (data: any) => void) => {
    webSocketClient.on(eventType, handler);
  }, []);

  const off = useCallback((eventType: EventType, handler: (data: any) => void) => {
    webSocketClient.off(eventType, handler);
  }, []);

  // Utility functions
  const ping = useCallback(() => {
    webSocketClient.ping();
  }, []);

  const getStatus = useCallback(() => {
    webSocketClient.getStatus();
  }, []);

  // Setup connection status listener
  useEffect(() => {
    const handleConnectionChange = (isConnected: boolean) => {
      setConnected(isConnected);
      if (!isConnected) {
        setSubscriptions([]);
      }
    };

    webSocketClient.onConnectionChange(handleConnectionChange);
    
    return () => {
      // Note: There's no removeConnectionHandler in our current implementation
      // This could be added to the MillDashWebSocket class if needed
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && !connected && !connecting) {
      connect();
    }
  }, [autoConnect, connected, connecting, connect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const contextValue: WebSocketContextType = {
    connected,
    connecting,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    subscriptions,
    on,
    off,
    ping,
    getStatus
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Custom hook for using WebSocket context
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

// Hook for subscribing to specific events
export const useWebSocketEvent = (
  eventType: EventType, 
  handler: (data: any) => void,
  dependencies: any[] = []
) => {
  const { on, off, connected } = useWebSocket();
  
  useEffect(() => {
    if (connected) {
      on(eventType, handler);
      return () => off(eventType, handler);
    }
  }, [eventType, connected, on, off, ...dependencies]);
};

// Hook for real-time dashboard data
export const useDashboardEvents = () => {
  const { subscribe, unsubscribe, connected } = useWebSocket();
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  
  useEffect(() => {
    if (connected) {
      subscribe([SubscriptionTypes.DASHBOARD, SubscriptionTypes.MACHINES]);
      return () => unsubscribe([SubscriptionTypes.DASHBOARD, SubscriptionTypes.MACHINES]);
    }
  }, [connected, subscribe, unsubscribe]);
  
  useWebSocketEvent(EventTypes.DASHBOARD_REFRESH, () => {
    setLastUpdate(new Date());
  });
  
  useWebSocketEvent(EventTypes.MACHINE_STATUS_UPDATE, () => {
    setLastUpdate(new Date());
  });
  
  return { lastUpdate };
};

// Hook for maintenance events
export const useMaintenanceEvents = () => {
  const { subscribe, unsubscribe, connected } = useWebSocket();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [ticketUpdates, setTicketUpdates] = useState<any[]>([]);
  
  useEffect(() => {
    if (connected) {
      subscribe([SubscriptionTypes.MAINTENANCE]);
      return () => unsubscribe([SubscriptionTypes.MAINTENANCE]);
    }
  }, [connected, subscribe, unsubscribe]);
  
  useWebSocketEvent(EventTypes.MAINTENANCE_ALERT, (data) => {
    setAlerts(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 alerts
  });
  
  useWebSocketEvent(EventTypes.TICKET_STATUS_CHANGE, (data) => {
    setTicketUpdates(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 updates
  });
  
  return { alerts, ticketUpdates };
};
