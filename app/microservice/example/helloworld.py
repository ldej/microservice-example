import asyncio
from microservice import ServiceManager, rpc


class GreetingService:
    name = "greeting_service"

    @rpc
    def hello(self, name):
        return "Hello, {}".format(name)

    @rpc
    def hello_again(self, name):
        return "Hello again, {}".format(name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    manager = ServiceManager(loop=loop)
    manager.add_service(GreetingService())

    loop.run_until_complete(manager.run())
    loop.run_forever()
    loop.close()

