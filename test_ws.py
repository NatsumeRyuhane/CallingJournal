
import asyncio
import websockets
import sys

async def test_websocket(url):
    print(f"Testing WebSocket connection to: {url}")
    try:
        async with websockets.connect(url) as websocket:
            print("Successfully connected to WebSocket!")
            await websocket.send('{"event": "connected", "protocol": "Call", "version": "1.0.0"}')
            print("Sent handshake message.")
            # Wait for a bit
            await asyncio.sleep(1)
            print("Closing connection.")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ws.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    asyncio.run(test_websocket(url))
