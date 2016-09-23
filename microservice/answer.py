import json

from nats.aio.client import Client as NATS
import asyncio


async def run(loop):
    nc = NATS()

    await nc.connect(io_loop=loop)

    async def help_request(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(subject=subject, reply=reply, data=data))
        for i in range(10):
            await nc.publish('natsresponse', json.dumps({'success': True, 'data': {'asd': i}}).encode())
            await asyncio.sleep(10)

    await nc.subscribe_async("natsrequest", cb=help_request)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
