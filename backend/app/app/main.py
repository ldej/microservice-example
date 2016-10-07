import asyncio

from microservice.rpc import ServiceCollector

from app.services.thing import ThingService
from app.services.greeting import GreetingService
from app import database


if __name__ == "__main__":
    database.create()

    loop = asyncio.get_event_loop()
    collector = ServiceCollector(loop=loop)

    # Add your services here
    collector.add_service(GreetingService())
    collector.add_service(ThingService())

    loop.run_until_complete(collector.run())
    loop.run_forever()
    loop.close()
