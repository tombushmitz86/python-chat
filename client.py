import websockets
import asyncio
import argparse
import attr
import json
import datetime


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, help="server address")
    parser.add_argument("-p", "--port", type=int, help="server port")
    args = parser.parse_args()

    def prompt_text(message):
        print('{0.timestamp} {0.username} > {0.text}'.format(message))

    async def handle_incoming(websocket):
        async for message in websocket:
            await prompt_text(Message.from_record(message))

    async def handle_outgoing(websocket):
        while True:
            text = input('> ')

            if text == '\q':
                print('Bye!')
                websocket.close()
                return

            await websocket.send(Message(
                text=text,
                timestamp=now(),
                username='tom',
            ).to_record())

    async def connect_to_server(host, port):
        # try:
        async with websockets.connect(f'ws://{host}:{port}') as websocket:
            print(
                'Welcome to the lonliest chat room in the world....\n' \
                'enter \'\q\' to quit the room',
            )
            username = input('What\'s your name?\n')

            incomings_task = asyncio.ensure_future(
                handle_incoming(websocket))
            outgoings_task = asyncio.ensure_future(
                handle_outgoing(websocket))
            done, pending = await asyncio.wait(
                [outgoings_task, incomings_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        # Could be all kinds raised from websockets, but for simplicity we catch all.
        # except Exception:
            # print(f'Could not connect to server at {host}:{port}')
            # return

    asyncio.get_event_loop().run_until_complete(connect_to_server(args.host, args.port))


if __name__ == '__main__':
    main()
