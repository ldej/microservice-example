import asyncio

from microservice.rpc import ServiceManager

from app.services.thing import ThingService
from app.services.greeting import GreetingService
from app.services.websockettest import WebsocketTestService
from app import database
import logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    database.create()

    loop = asyncio.get_event_loop()
    manager = ServiceManager(loop=loop)

    # Add your services here
    manager.add_service(GreetingService())
    manager.add_service(ThingService())
    manager.add_service(WebsocketTestService())

    loop.run_until_complete(manager.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        logger.debug("Caught keyboard interrupt")
    finally:
        loop.stop()
        loop.close()

