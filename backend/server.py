import socketio
import json
import asyncio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

background_proc = lambda x:x

#CACHE!!!
#CACHE = []

# Keep track of connected clients
connected_clients = set()

async def send_data_to_all(data):
    #CACHE.append(data)
    await sio.emit('message', data)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    connected_clients.add(sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    connected_clients.discard(sid)

onMessageCallbacks = []

def registerEventOnMessage(event):
    onMessageCallbacks.append(event)

@sio.event
async def message(sid, data):
    if data=="ping":
        return
    for f in onMessageCallbacks:
        f(data)
    sio.start_background_task(background_proc, data)

    return data

registerEventOnMessage(print)

def start_server(other):
    registerEventOnMessage(other)
    global background_proc
    background_proc = other
    web.run_app(app, port=4000)
