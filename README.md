# Microservice example

A [nats](http://nats.io/) , [asyncio](https://docs.python.org/dev/library/asyncio.html), [aiohttp](https://aiohttp.readthedocs.io/en/stable/),
[SqlAlchemy](https://docs.sqlalchemy.org/en/latest/) example for creating a microservice. Support for websockets using 
[WAMP](https://github.com/wamp-proto/wamp-proto) is included.

## Installation

```bash
git clone https://github.com/ldej/microservice-example
cd ./microservice-example
docker-compose build
```

## Basic usage
Start the project
```bash
docker-compose up
```

Try the basic greeting service:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello' -d '[["Bob"]]'
```

See the asyncio in action. The ```greeting_service.hello_sleep``` call will sleep for 10 seconds.
So open two terminals, in the first one:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello_sleep' -d '[[], {"name": "Sleepy Bob"}]'
```
And in the second:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello' -d '[["Awake Bob"]]'
```
The second call should return before the first call.

Or make a call to create a thing:
```bash
curl -X POST 'http://127.0.0.1:5000/thing_service.create_thing' -d '[[], {"name": "Alice"}]'
```

See that a thing is created:
```bash
curl -X POST 'http://127.0.0.1:5000/thing_service.get_things'
```

### Websockets
Make sure the project is started. Open ```frontend/index.html```. In the subscribe section, the RPC input will be 
filled with ```websocket_test.websocket_test```. When pressing send, the websocket will be subscribed to that 
message on nats. There are two ways to confirm that it works. The first is to do:
```bash
curl -X POST 'http://127.0.0.1:5000/websocket_test.hello_websocket' -d '[["websockets"], {"are": "awesome"}]'
```
This is a normal HTTP POST call. The call ```websocket_test.hello_websocket``` will send a message over nats on 
channel ```websocket_test.websocket_test``` and it will forward all arguments to it as well. The browser will then 
show the message that was sent.

The second way to confirm is by using the publish section of the frontend. This will send the message to the backend 
over the websocket (instead of HTTP/POST). And it should give the same result in the frontend as the HTTP POST call.

### Args and kwargs
The arguments sent to a call consist of three parts. The structure is ```[Args|list, KwArgs|dict]```.
The arguments and keyword arguments will be unpacked in the ```@rpc``` calls.

## Example rpc

The structure of services and the ```@rpc``` decorator have been ~~stolen from~~ inspired by [Nameko](https://nameko.readthedocs.io/en/stable/). 
Where Nameko uses AMQP, this project uses nats. 

An example of an rpc is the greeting service:
```python3
import asyncio

from microservice.rpc import rpc


class GreetingService:
    name = "greeting_service"

    @rpc
    async def hello(self, first_name, last_name='') -> ([], {}):
        return ["Hello, {first_name} {last_name}".format(first_name=first_name, last_name=last_name)], {}
```

The ```greeting_service.hello``` rpc can be called by:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello' -d '[["Bob"], {"last_name": "Ross"}]'
```
And it will return:
```bash
[["Hello, Bob Ross"], {}]
```

The rpc can be invoked over nats as well. As subject choose ```greeting_service.hello``` and as data set ```'[["Bob"], {"last_name": "Ross"}]'```. 
The same result should be returned. 

# Development

## Watchdog
When running ```docker-compose up```, the ```docker-compose.yml``` file is used. This file changes the 
```http-api``` and ```app``` services so they will mount the local code, and reload automatically when
any of the ```.py``` files in the folders are updated.

## Todo
 - Packaging

### Websocket WAMP
 - 'wamp.2.msgpck'
 - session ids
 - publication ids
 - javascript example
 - optional args/kwargs handling (remove arguments when empty)

### Microservice rpc
 - publication ids
 - apispec/swagger
 - [Queues](https://nats.io/documentation/concepts/nats-queueing/)
 - [Schemas](https://marshmallow.readthedocs.io/en/latest/) for rpcs
 - Authentication
 - Migrations

### Code generation
 - Use OLE to generate SqlAlchemy models, Schemas, javascript models

### Docker
 - nginx/caddy/letsencrypt

### High availability
An example with multiple http-apis, a cluster of nats servers and a bunch of app instances.
