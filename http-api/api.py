import logging
import json
import asyncio

from aiohttp import WSMsgType, HttpBadRequest
from aiohttp import web
from nats.aio.client import Client as NATS

NATS_URL = 'nats://nats:4222'


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


async def call(request):

    con = NATS()
    await con.connect(io_loop=loop, servers=[NATS_URL])

    if await request.text():
        try:
            data = await request.json()
        except json.decoder.JSONDecodeError as e:
            raise HttpBadRequest(e)
    else:
        data = {}

    rpc = request.match_info.get('rpc')
    logger.debug('Received http request: {}'.format(rpc))

    msg = await con.timed_request(rpc, json.dumps(data).encode(), timeout=60)

    return web.json_response(json.loads(msg.data.decode()))


class WebSocketHandler:
    ws = None
    con = None

    async def wshandler(self, request):
        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)

        self.con = NATS()
        await self.con.connect(io_loop=loop, servers=[NATS_URL])

        await asyncio.gather(self.handle_ws(), self.handle_nats())

        return self.ws

    async def handle_nats(self):
        async def process_message(message):
            self.ws.send_json(json.loads(message.data.decode()))

        await self.con.subscribe_async('natsresponse', cb=process_message)

    async def handle_ws(self):
        while True:
            msg = await self.ws.receive()
            if msg.type == WSMsgType.TEXT:
                await self.con.publish('natsrequest', json.dumps({'asd': 1}).encode())


if __name__ == "__main__":
    logger.debug("Starting http-api")

    loop = asyncio.get_event_loop()

    app = web.Application(loop=loop)
    handler = WebSocketHandler()
    app.router.add_get('/websocket', handler.wshandler)
    app.router.add_post('/{rpc}', call)

    logger.debug("Http-api started")
    web.run_app(app, port=5000)
