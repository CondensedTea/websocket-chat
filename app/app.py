import asyncio
from typing import Dict, List

import aioredis
from aioredis import Channel, ConnectionsPool
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


HISTORY_CHANNEL = 'history'

users = []

redis_url = ('redis', 6379)


async def get_redis() -> ConnectionsPool:
    pool = await aioredis.create_redis_pool(redis_url)
    return pool


async def reader(channel: Channel, socket: WebSocket) -> None:
    async for message in channel.iter():
        await socket.send_text(message.decode('utf-8'))


async def broadcast(
    r: ConnectionsPool, user_list: List[str], name: str, message: str
) -> None:
    for user in user_list:
        ch = f'channel:{user}'
        if user != name:
            await r.publish(ch, message)


async def save_history(r: ConnectionsPool, message: str) -> None:
    await r.rpush(HISTORY_CHANNEL, message)
    await r.ltrim(HISTORY_CHANNEL, 0, 50)


async def close_redis(r: ConnectionsPool) -> None:
    r.close()
    await r.wait_closed()


@app.get('/')
async def history(r: ConnectionsPool = Depends(get_redis)) -> Dict[str, List[str]]:
    msg_history = await r.lrange(HISTORY_CHANNEL, 0, -1)
    return {'messages': msg_history}


@app.websocket('/ws/{name}')
async def websocket_endpoint(
    websocket: WebSocket, name: str, r: ConnectionsPool = Depends(get_redis)
) -> None:
    await websocket.accept()
    if name in users:
        await websocket.send_text(
            '[Error]: Name already taken, please reconnect with different name'
        )
        await websocket.close(code=1000)
        await close_redis(r)
        return
    await websocket.send_text(f'Welcome to chat, {name}')
    [channel] = await r.subscribe(f'channel:{name}')
    asyncio.get_running_loop().create_task(reader(channel, websocket))
    users.append(name)
    try:
        while True:
            msg = await websocket.receive_text()
            signed_msg = f'{name}: {msg}'
            await save_history(r, signed_msg)
            await broadcast(r, users, name, signed_msg)
    except WebSocketDisconnect:
        users.remove(name)
        await broadcast(r, users, name, f'{name} left the chat')
    finally:
        await close_redis(r)
