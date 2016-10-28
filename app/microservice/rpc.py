from collections import namedtuple

import asyncio
from nats.aio.client import Client as NatsClient
import json
import inspect
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


NATS_URL = 'nats://nats:4222'

RpcService = namedtuple('RpcService', ['name', 'methods'])


class MessageData:
    def __init__(self, args=None, kwargs=None):
        self.args = args or []
        self.kwargs = kwargs or {}


class ServiceManager:

    def __init__(self, loop):
        self.services = []
        self.loop = loop
        self.nats_client = None

    def add_service(self, instance):
        service_class = type(instance)
        service_name = getattr(service_class, 'name', None)
        if not service_name:
            raise Exception("Service {} does not have a property 'name'.".format(service_class))

        methods = inspect.getmembers(instance, predicate=inspect.ismethod)
        instance.send_message = self.send_message

        def is_rpc(method_tuple):
            method_name, method = method_tuple
            return getattr(method, 'rpc', False)

        self.services.append(RpcService(name=service_name, methods=filter(is_rpc, methods)))

    async def run(self):
        await self.start_nats()

        for service in self.services:
            logger.debug("starting service: {}".format(service.name))
            for method_name, method in service.methods:
                logger.debug("\t - {}".format(method_name))
                rpc_name = "{service_name}.{method_name}".format(service_name=service.name, method_name=method_name)
                await self.nats_client.subscribe_async(rpc_name, queue=rpc_name, cb=self.nats_wrapper(method))

    def nats_wrapper(self, fn):
        async def callback(msg):
            message_data = MessageData(*json.loads(msg.data.decode()))

            # Do something with message_data options? Login sessions?

            results = await fn(*message_data.args, **message_data.kwargs)
            if type(results) is not tuple or len(results) != 2 or type(results[0]) != list or type(results[1]) != dict:
                raise TypeError('Function should result a tuple with a list and a dict. Example: ([], {})')

            if msg.reply:
                await self.nats_client.publish(msg.reply, json.dumps([*results]).encode())
        return callback

    async def start_nats(self):
        self.nats_client = NatsClient()
        await self.nats_client.connect(io_loop=self.loop, servers=[NATS_URL])

    async def send_message(self, channel, args, kwargs):
        await self.nats_client.publish(channel, json.dumps([args, kwargs]).encode())

    @classmethod
    def decorator(cls, method):
        method.rpc = True
        return method


rpc = ServiceManager.decorator
