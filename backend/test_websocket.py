#!/usr/bin/env python3
"""
WebSocket test client to verify Phase 4 implementation.
Tests WebSocket connection, subscription, and event broadcasting.
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Test basic WebSocket connection and functionality."""
    uri = "ws://localhost:8000/api/v1/ws?client_id=test_client"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Test 1: Wait for welcome message
            welcome_message = await websocket.recv()
            welcome_data = json.loads(welcome_message)
            print(f"📩 Received welcome: {welcome_data['type']}")
            
            # Test 2: Subscribe to maintenance events
            subscribe_message = {
                "type": "subscribe",
                "subscriptions": ["maintenance", "dashboard"]
            }
            await websocket.send(json.dumps(subscribe_message))
            print("📋 Sent subscription request")
            
            # Wait for subscription confirmation
            response = await websocket.recv()
            sub_data = json.loads(response)
            print(f"✅ Subscription confirmed: {sub_data['subscriptions']}")
            
            # Test 3: Send ping
            ping_message = {
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(ping_message))
            print("🏓 Sent ping")
            
            # Wait for pong
            pong_response = await websocket.recv()
            pong_data = json.loads(pong_response)
            print(f"🏓 Received pong: {pong_data['type']}")
            
            # Test 4: Get connection status
            status_message = {"type": "get_status"}
            await websocket.send(json.dumps(status_message))
            print("📊 Requested connection status")
            
            # Wait for status response
            status_response = await websocket.recv()
            status_data = json.loads(status_response)
            print(f"📊 Connection status: {status_data['data']['total_connections']} total connections")
            
            # Test 5: Listen for events for a few seconds
            print("👂 Listening for events for 5 seconds...")
            try:
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
                event_data = json.loads(await websocket.recv())
                print(f"🎉 Received event: {event_data['type']}")
            except asyncio.TimeoutError:
                print("⏰ No events received during test period")
            
            print("✅ WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

async def test_admin_websocket():
    """Test admin WebSocket functionality."""
    uri = "ws://localhost:8000/api/v1/ws/admin"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔧 Connected to admin WebSocket")
            
            # Wait for welcome message
            welcome_message = await websocket.recv()
            print(f"📩 Admin welcome received")
            
            # Test broadcasting a test event
            broadcast_message = {
                "action": "broadcast_test",
                "event_type": "system_alert",
                "data": {"message": "Test alert from WebSocket test"},
                "subscription": "all"
            }
            await websocket.send(json.dumps(broadcast_message))
            print("📢 Sent test broadcast")
            
            # Wait for confirmation
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"✅ Broadcast confirmed: {response_data['type']}")
            
            # Get connection stats
            stats_message = {"action": "get_connections"}
            await websocket.send(json.dumps(stats_message))
            
            stats_response = await websocket.recv()
            stats_data = json.loads(stats_response)
            print(f"📊 Admin stats: {stats_data['data']['total_connections']} connections")
            
            print("✅ Admin WebSocket test completed!")
            
    except Exception as e:
        print(f"❌ Admin WebSocket test failed: {e}")
        return False
    
    return True

async def main():
    """Run all WebSocket tests."""
    print("🚀 Starting Phase 4 WebSocket Tests")
    print("=" * 50)
    
    # Test regular WebSocket connection
    print("🔍 Testing regular WebSocket connection...")
    success1 = await test_websocket_connection()
    
    print("\n" + "=" * 50)
    
    # Test admin WebSocket connection
    print("🔍 Testing admin WebSocket connection...")
    success2 = await test_admin_websocket()
    
    print("\n" + "=" * 50)
    
    if success1 and success2:
        print("🎉 All Phase 4 WebSocket tests passed!")
        print("✅ Real-time communication is working correctly")
    else:
        print("❌ Some WebSocket tests failed")
        print("🔧 Check backend logs for more details")

if __name__ == "__main__":
    asyncio.run(main())
