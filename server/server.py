import datetime
import attr
import json
import argparse
import websockets
import logging
import asyncio


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)

log = logging.getLogger('server')


def now():
    return datetime.datetime.now().isoformat()


class Message:

    def __init__(self, text, username, timestamp):
        self.username = username
        self.text = text
        self.timestamp = timestamp

    @classmethod
    def from_record(cls, data):
        data = json.loads(data)
        return cls(
            text=data['text'],
            username=data['username'],
            timestamp=data['timestamp'],
        )

    def to_record(self):
        """str representation"""
        return json.dumps({
            'timestamp': self.timestamp,
            'text': self.text,
            'username': self.username,
        })


@attr.s(slots=True)
class Client:
    name = attr.ib()
    joined_at = attr.ib()
    last_messages = attr.ib()


def do_something(message):
    log.info("got a new message")


class ChatServer:
    def __init__(self, host, port):
        self.clients = {}  # {websocket: Client}
        self.server = websockets.serve(self.handle_messages, host, port)
        log.info('Starting server at {}, {}'.format(host, port))

    async def send_to_all(self, message):
        for client in self.clients.keys():
            print("sending to client")
            await client.send(message.to_record())

    async def handle_user_left(self, websocket):
        message = Message(
            text='{} has left the chat'.format(self.clients[websocket].name),
            username='admin',
            timestamp=now(),
        )
        log.info(message.text)
        for ws, client in self.clients.items():
            if ws != websocket:
                await ws.send(message.to_record())

        del self.clients[websocket]

    async def handle_new_user(self, websocket, message):
        message = Message.from_record(message)
        client = Client(
            name=message.username,
            joined_at=message.timestamp,
            last_messages=[message.text],
        )
        welcome_text = (
                'Welcome to the chat!\n there are currently {} people chatting in this room: {}'
                .format(
                    len(self.clients),
                    '\n'.join([c.name for c in self.clients.values()]),
                )
            )
        greet_message = Message(
            text=welcome_text,
            timestamp=now(),
            username="admin",
        )

        await websocket.send(greet_message.to_record())

        log.info('{} has joined the chat'.format(client.name))
        await self.send_to_all(Message(
            username='admin',
            text='{} has joined the chat'.format(client.name),
            timestamp=now(),
        ))

        self.clients[websocket] = client

    # Handle a connection from a single client.
    async def handle_messages(self, websocket, path):
        log.info('connection established from {}'.format(websocket.origin))
        try:
            async for _incoming_message in websocket:
                if websocket not in self.clients:
                    await self.handle_new_user(websocket, _incoming_message)

                message = Message.from_record(_incoming_message)
                await self.send_to_all(message)
        except websockets.exceptions.ConnectionClosed:
            if websocket in self.clients:
                await self.handle_user_left(websocket)
            return

        await self.handle_user_left(websocket)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default='0.0.0.0', help="host to serve from")
    parser.add_argument("-p", "--port", default=3030, help="port to serve on")
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    args = parser.parse_args()

    server = ChatServer(args.host, args.port)
    asyncio.get_event_loop().run_until_complete(server.server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
