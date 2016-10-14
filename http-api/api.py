import logging
import json
import asyncio

from aiohttp import WSMsgType, HttpBadRequest
from aiohttp import web
from nats.aio.client import Client as NATS

from websocket_handler import WebSocketHandler

NATS_URL = 'nats://nats:4222'
NATS_CALL_TIMEOUT = 60  # seconds


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


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
