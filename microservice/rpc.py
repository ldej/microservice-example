from collections import namedtuple

from nats.aio.client import Client as NatsClient
import json
import inspect

RpcService = namedtuple('RpcService', ['name', 'methods'])


class ServiceCollector:
    services = []
    nats_client = None

    def __init__(self, loop):
        self.loop = loop

    def add_service(self, instance):
        service_class = type(instance)
        service_name = getattr(service_class, 'name', None)
        if not service_name:
            raise Exception("Service {} does not have a property 'name'.".format(service_class))

        methods = inspect.getmembers(instance, predicate=inspect.ismethod)

        def is_rpc(method_tuple):
            method_name, method = method_tuple
            return getattr(method, 'rpc', False)

        self.services.append(RpcService(name=service_name, methods=filter(is_rpc, methods)))

    async def run(self):
        await self.start_nats()

        for service in self.services:
            print("starting service: {}".format(service.name))
            for method_name, method in service.methods:
                print("\t - {}".format(method_name))
                rpc_name = "{service_name}.{method_name}".format(service_name=service.name, method_name=method_name)
                await self.nats_client.subscribe_async(rpc_name, queue=rpc_name, cb=self.nats_wrapper(method))

    def nats_wrapper(self, fn):
        async def callback(msg):
            data = json.loads(msg.data.decode())
            result = fn(**data)
            await self.nats_client.publish(msg.reply, json.dumps(result).encode())
        return callback

    async def start_nats(self):
        self.nats_client = NatsClient()
        await self.nats_client.connect(io_loop=self.loop)

    @classmethod
    def decorator(cls, method):
        method.rpc = True
        return method


rpc = ServiceCollector.decorator
