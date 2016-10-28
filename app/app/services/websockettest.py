from microservice.rpc import rpc
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class WebsocketTestService:
    name = 'websocket_test'

    @rpc
    async def hello_websocket(self, *args, **kwargs) -> ([], {}):
        await self.send_message('websocket_test.websocket_test', args, kwargs)
        return ["Look at your browser"], {}
