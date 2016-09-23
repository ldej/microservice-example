"""
TODO:
 - Some way to show the websockets potential.
     - Subscribe to a certain channel, with the websocket. A callback from another channel should post something back
       in the websocket channel. So like somebody is posting information, and you get a message of that via
       websocket.
     - Make a simple websocket webpage with input fields for: the service you want to call, the data you want to
       send. And a way to select which websocket channel you want to subscribe to. Maybe subscribe to more channels
       over the same websocket?

 - Add a way to send messages to other services.
 - Use marshmallow schema's for loading and dumping data at service calls.
 - Add a javascript way to use these schema's and invoke services.
 - Add an easy service call test thing.

"""


import json
import asyncio

from aiohttp import WSMsgType
from aiohttp import web
from nats.aio.client import Client as NATS


async def call(request):

    con = NATS()
    await con.connect(io_loop=loop, servers=['nats://localhost:4222'])

    data = await request.json()
    rpc = request.match_info.get('rpc')

    msg = await con.timed_request(rpc, json.dumps(data).encode())

    return web.json_response(msg.data.decode())


class WebSocketHandler:
    ws = None
    con = None

    async def wshandler(self, request):
        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)
        print('Got a websocket request')

        self.con = NATS()
        await self.con.connect(io_loop=loop, servers=['nats://localhost:4222'])

        await asyncio.gather(self.handle_ws(), self.handle_nats())

        return self.ws

    async def handle_nats(self):
        async def process_message(message):
            print(message.data)
            self.ws.send_json(json.loads(message.data.decode()))

        await self.con.subscribe_async('natsresponse', cb=process_message)

    async def handle_ws(self):
        while True:
            msg = await self.ws.receive()
            print(msg)
            if msg.type == WSMsgType.TEXT:
                await self.con.publish('natsrequest', json.dumps({'asd': 1}).encode())


loop = asyncio.get_event_loop()

app = web.Application(loop=loop)
handler = WebSocketHandler()
app.router.add_get('/websocket', handler.wshandler)
app.router.add_post('/{rpc}', call)
app.router.add_get('/{rpc}', call)

web.run_app(app)
