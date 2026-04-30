"""
Simple WebSocket broadcast server for the web frontend.
Run: python ws_server.py
Requires: websockets (pip install websockets)
"""
import asyncio
import json
import websockets

PORT = 6789

clients = set()
names = {}

def register(ws):
    clients.add(ws)

async def unregister(ws):
    clients.discard(ws)
    name = names.pop(ws, None)
    if name:
        await broadcast({'type':'system','text':f"{name} left the chat"})

async def broadcast(obj):
    if clients:
        data = json.dumps(obj)
        await asyncio.wait([c.send(data) for c in clients])

async def handler(ws, path):
    register(ws)
    try:
        async for message in ws:
            try:
                obj = json.loads(message)
            except Exception:
                continue

            if obj.get('type') == 'join':
                names[ws] = obj.get('name','Guest')
                await broadcast({'type':'system','text':f"{names[ws]} joined the chat"})
            elif obj.get('type') == 'msg':
                name = names.get(ws,'Guest')
                await broadcast({'type':'msg','name':name,'text':obj.get('text','')})
    finally:
        await unregister(ws)

def main():
    print(f"Starting WebSocket server on ws://localhost:{PORT}")
    start_server = websockets.serve(handler, '0.0.0.0', PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print('\nShutting down')

if __name__ == '__main__':
    main()
