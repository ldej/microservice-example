from microservice.rpc import rpc


class GreetingService:
    name = "greeting_service"

    @rpc
    def hello(self, name):
        return "Hello, {}".format(name)
