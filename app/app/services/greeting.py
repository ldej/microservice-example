import asyncio
from microservice.rpc import rpc

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class GreetingService:
    name = "greeting_service"

    @rpc
    async def hello(self, data):
        return "Hello, {}".format(data.get('name'))

    @rpc
    async def hello_sleep(self, data):
        logger.debug('waiting for 10 seconds')
        await asyncio.sleep(10)
        logger.debug('waited')
        return "Hello, {}".format(data.get('name'))
