# Microservice example

A nats, asyncio, aiohttp, sqlalchemy example for creating a microservice.

## Installation

```bash
git clone https://github.com/ldej/microservice-example
docker-compose build
```

## Basic usage

```bash
docker-compose up
```

Make a call to create a thing:
```bash
curl -X POST 'http://127.0.0.1:5000/thing_service.create_thing' -d '{"name": "Alice"}'
```

See that a thing is created:
```bash
curl -X POST 'http://127.0.0.1:5000/thing_service.get_things'
```

Try the basic greeting service:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello' -d '{"name": "Bob"}'
```

See the asyncio in action. The ```greeting_service.hello_sleep``` call will sleep for 10 seconds.
So open two terminals, in the first one:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello_sleep' -d '{"name": "Sleepy Bob"}'
```
And in the second:
```bash
curl -X POST 'http://127.0.0.1:5000/greeting_service.hello' -d '{"name": "Awake Bob"}'
```
The second call should return before the first call.

## TODO
 - Some way to show the websockets potential.
     - Subscribe to a certain channel, with the websocket. A callback from another channel should post something back
       in the websocket channel. So like somebody is posting information, and you get a message of that via
       websocket.
     - Make a simple websocket webpage with input fields for: the service you want to call, the data you want to
       send. And a way to select which websocket channel you want to subscribe to. Maybe subscribe to more channels
       over the same websocket?

 - Add a way to send messages to other services.
 - Add a javascript way to use these schema's and invoke services.
 - Add an easy service call test thing.
