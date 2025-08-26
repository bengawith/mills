/**
 * WebSocket connection status indicator component.
 * Shows the real-time connection status and provides manual controls.
 */

import React from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Wifi, WifiOff, Loader2, Activity, RefreshCw } from 'lucide-react';

interface ConnectionStatusProps {
  showControls?: boolean;
  compact?: boolean;
  className?: string;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  showControls = false, 
  compact = true,
  className = ''
}) => {
  const { connected, connecting, connect, disconnect, ping, subscriptions } = useWebSocket();

  const getStatusIcon = () => {
    if (connecting) {
      return <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />;
    }
    if (connected) {
      return <Wifi className="h-4 w-4 text-green-500" />;
    }
    return <WifiOff className="h-4 w-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (connecting) return 'Connecting...';
    if (connected) return 'Connected';
    return 'Disconnected';
  };

  const getStatusColor = () => {
    if (connecting) return 'yellow';
    if (connected) return 'green';
    return 'red';
  };

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        {getStatusIcon()}
        <Badge variant={connected ? 'default' : 'destructive'}>
          {getStatusText()}
        </Badge>
        {connected && (
          <Badge variant="secondary" className="text-xs">
            {subscriptions.length} subs
          </Badge>
        )}
        {showControls && (
          <Button
            size="sm"
            variant="ghost"
            onClick={ping}
            disabled={!connected}
            className="h-6 w-6 p-0"
          >
            <Activity className="h-3 w-3" />
          </Button>
        )}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-medium">{getStatusText()}</span>
                <Badge 
                  variant={connected ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  Real-time
                </Badge>
              </div>
              {connected && (
                <p className="text-sm text-muted-foreground">
                  Subscribed to {subscriptions.length} event types
                </p>
              )}
            </div>
          </div>
          
          {showControls && (
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                onClick={ping}
                disabled={!connected}
              >
                <Activity className="h-4 w-4 mr-2" />
                Ping
              </Button>
              
              {connected ? (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={disconnect}
                >
                  <WifiOff className="h-4 w-4 mr-2" />
                  Disconnect
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={connect}
                  disabled={connecting}
                >
                  {connecting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  {connecting ? 'Connecting...' : 'Connect'}
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ConnectionStatus;
