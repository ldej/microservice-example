import asyncio
from rpc import ServiceCollector, rpc


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

    collector = ServiceCollector(loop=loop)
    collector.add_service(GreetingService())

    loop.run_until_complete(collector.run())
    loop.run_forever()
    loop.close()

