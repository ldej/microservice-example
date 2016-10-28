import asyncio
import logging

from microservice.rpc import rpc


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class GreetingService:
    name = "greeting_service"

    @rpc
    async def hello(self, first_name, last_name='') -> ([], {}):
        return ["Hello, {first_name} {last_name}".format(first_name=first_name, last_name=last_name)], {}

    @rpc
    async def hello_sleep(self, name=None) -> ([], {}):
        logger.debug('waiting for 10 seconds')
        await asyncio.sleep(10)
        return ["Hello, {}".format(name)], {}
