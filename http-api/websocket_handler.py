import logging
import json
import asyncio

from aiohttp import WSMsgType, HttpBadRequest
from aiohttp import web
from nats.aio.client import Client as NATS

from wamp import MessageType

NATS_URL = 'nats://nats:4222'
NATS_CALL_TIMEOUT = 60  # seconds


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class WebSocketHandler:
    def __init__(self, loop):
        self.ws = None
        self.con = None
        self.loop = loop

    async def wshandler(self, request):
        self.ws = web.WebSocketResponse(protocols=('wamp.2.json',))
        await self.ws.prepare(request)

        logger.debug("Incoming websocket")
        self.con = NATS()
        await self.con.connect(io_loop=self.loop, servers=[NATS_URL])

        await asyncio.gather(self.handle_ws())

        return self.ws

    async def subscribe(self, topic):
        logger.debug("Websocket subscribed to: {}".format(topic))
        return await self.con.subscribe_async(topic, cb=self.subscribe_callback)

    async def subscribe_callback(self, message):
        details = message.data.get('details', {})
        args = message.data.get('args', [])
        kwargs = message.data.get('kwargs', {})
        await self.reply([MessageType.EVENT, message.subject, 1, details, args, kwargs])

    async def unsubscribe(self, subscription_id):
        await self.con.unsubscribe(subscription_id)

    async def publish(self, topic, data):
        await self.con.publish(topic, json.dumps(data).encode())

    async def handle_ws(self):
        while True:
            msg = await self.ws.receive()
            if msg.type == WSMsgType.TEXT:
                message = json.loads(msg.data)
                await self.process_message(message)

    async def reply(self, message):
        self.ws.send_json(message)

    async def call(self, procedure, data):
        return await self.con.timed_request(procedure, json.dumps(data).encode(), timeout=NATS_CALL_TIMEOUT)

    async def process_message(self, message):
        logger.debug('Received message: {}'.format(message))
        try:
            message_type, *payload = message
        except TypeError:
            await self.reply([MessageType.ERROR, {'message': 'Unable to read message.'}])
            return

        if message_type == MessageType.HELLO:
            realm, details = payload
            await self.reply([MessageType.WELCOME, 1])

        elif message_type == MessageType.ABORT:
            details, reason = payload
            logger.debug('Establishing session aborted, reason: {}'.format(reason))

        elif message_type == MessageType.GOODBYE:
            details, reason = payload
            logger.debug('Closing session, reason: {}'.format(reason))
            await self.reply([MessageType.GOODBYE])

        elif message_type == MessageType.ERROR:
            request_type, *rest = payload
            logger.debug('Received ERROR: {}'.format(payload))

        elif message_type == MessageType.PUBLISH:
            request_id, options, topic, *rest = payload
            if len(rest) == 1:
                args, kwargs = [*rest, None]
            elif len(rest) == 2:
                args, kwargs = rest
            else:
                return
                # Error
            await self.publish(topic, [args, kwargs])
            await self.reply([MessageType.PUBLISHED, request_id, 1])

        elif message_type == MessageType.SUBSCRIBE:
            request_id, options, topic = payload
            subscription_id = await self.subscribe(topic)
            await self.reply([MessageType.SUBSCRIBED, request_id, subscription_id])

        elif message_type == MessageType.UNSUBSCRIBE:
            request_id, subscription_id = payload
            await self.unsubscribe(subscription_id)
            await self.reply([MessageType.UNSUBSCRIBED, request_id])

        elif message_type == MessageType.CALL:
            request_id, options, procedure, args, kwargs = payload
            result = await self.call(procedure, [args, kwargs])
            await self.reply([MessageType.RESULT, request_id, {}, result])

        else:  # Not implemented
            await self.reply([MessageType.ERROR, {'message': 'Not supported/implemented'}])
