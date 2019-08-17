import asyncio
import websockets
import json
import sys
from .core import parse_problem

PORT = 12358


async def parse(websocket, path):
    data = await websocket.recv()
    if data == 'exit':
        sys.exit(0)
    data = json.loads(data)
    msg = json.dumps(parse_problem(data['url'], data['data']), indent=4)
    await websocket.send(msg)


def start_server():
    server = websockets.serve(parse, 'localhost', PORT)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


def stop_server():
    async def send_stop():
        async with websockets.connect('ws://localhost:%i' % PORT) as websocket:
            await websocket.send('exit')

    asyncio.get_event_loop().run_until_complete(send_stop())


if __name__ == '__main__':
    start_server()
