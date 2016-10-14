import logging
import json
import asyncio

from aiohttp import WSMsgType, HttpBadRequest
from aiohttp import web
from nats.aio.client import Client as NATS

NATS_URL = 'nats://nats:4222'
NATS_CALL_TIMEOUT = 60  # seconds


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
    logger.debug('=Received http request: {0} {1}'.format(rpc, data))
    msg = await con.timed_request(rpc, json.dumps(data).encode(), timeout=NATS_CALL_TIMEOUT)

    return web.json_response(json.loads(msg.data.decode()))


class WebSocketHandler:
    def __init__(self, loop):
        self.ws = None
        self.con = None
        self.loop = loop

    async def wshandler(self, request):
        self.ws = web.WebSocketResponse()
        await self.ws.prepare(request)

        self.con = NATS()
        await self.con.connect(io_loop=self.loop, servers=[NATS_URL])

        await asyncio.gather(self.handle_ws())

        return self.ws

    async def process_message(self, message):
        self.ws.send_json(json.loads(message.data.decode()))

    async def subscribe(self, messages):
        logger.debug("Websocket subscribed to: {}".format(messages))
        for message in messages:
            await self.con.subscribe_async(message, cb=self.process_message)

    async def handle_ws(self):
        while True:
            msg = await self.ws.receive()
            if msg.type == WSMsgType.TEXT:
                message_data = json.loads(msg.data)
                action = message_data.get('action')
                if action == 'subscribe':
                    await self.subscribe(message_data.get('rpcs', []))
                elif action == 'publish':
                    rpc = message_data.get('rpc')
                    data = message_data.get('data')
                    await self.con.publish(rpc, data.encode())
                else:
                    self.ws.send_json({'error': True, 'message': "Unknown action '{}'".format(action)})


if __name__ == "__main__":
    logger.debug("Starting http-api")

    loop = asyncio.get_event_loop()

    app = web.Application(loop=loop)

    websocket_handler = WebSocketHandler(loop=loop)
    app.router.add_get('/websocket', websocket_handler.wshandler)

    app.router.add_post('/{rpc}', call)

    logger.debug("Http-api started")
    web.run_app(app, port=5000)
