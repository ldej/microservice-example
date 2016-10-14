from microservice.rpc import rpc
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class WebsocketTestService:
    name = 'websocket_test'

    @rpc
    async def websocket_test(self, data):
        logger.debug('Received websocket_test.websocket_test call')
        return {'yay': 'yay'}

    @rpc
    async def hello_websocket(self, data):
        await self.send_message('websocket_test.websocket_test', data)
