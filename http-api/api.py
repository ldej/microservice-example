import logging
import json
import asyncio
import datetime

from aiohttp import WSMsgType, HttpBadRequest
from aiohttp import web
import aiohttp
from nats.aio.client import Client as NATS

from websocket_handler import WebSocketHandler

NATS_URL = 'nats://nats:4222'
NATS_SERVICE_URL = 'nats://nats:8222/connz?subs=1'
NATS_CALL_TIMEOUT = 60  # seconds


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

subscriptions = []
last_requested = datetime.datetime.now() - datetime.timedelta(minutes=1)


async def in_active_subscriptions(rpc):
    global subscriptions
    global last_requested

    if last_requested < datetime.datetime.now() - datetime.timedelta(minutes=1):
        subscriptions = await get_subscriptions()
        last_requested = datetime.datetime.now()

    return rpc in subscriptions


async def get_subscriptions():
    async with aiohttp.ClientSession() as session:
        async with session.get(NATS_SERVICE_URL) as response:
            result = await response.json()
            return {sub for connection in result.get('connections') for sub in connection.get('subscriptions_list', [])}


async def call(request):
    """Process a call.

    HTTP only supports request/response. Therefore you can only request/response.

    :param request:
    :return:
    """

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

    if not await in_active_subscriptions(rpc):
        logger.debug('Unknown RPC: {}'.format(rpc))
        raise HttpBadRequest("Unknown RPC: '{0}'. Available rpcs: {1}".format(rpc, subscriptions))

    logger.debug('=Received http request: {0} {1}'.format(rpc, data))
    msg = await con.timed_request(rpc, json.dumps(data).encode(), timeout=NATS_CALL_TIMEOUT)

    return web.json_response(json.loads(msg.data.decode()))


if __name__ == "__main__":
    logger.debug("Starting http-api")

    loop = asyncio.get_event_loop()

    app = web.Application(loop=loop)

    websocket_handler = WebSocketHandler(loop=loop)
    app.router.add_get('/websocket', websocket_handler.wshandler)

    app.router.add_post('/{rpc}', call)

    logger.debug("Http-api started")
    web.run_app(app, port=5000)
