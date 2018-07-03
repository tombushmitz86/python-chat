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

    async def connect_to_server(host, port):
        # try:
        async with websockets.connect(f'ws://{host}:{port}') as websocket:
            print(
                'Welcome to the lonliest chat room in the world....\n' \
                'enter \'\q\' to quit the room',
            )
            username = input('What\'s your name?\n')

            await websocket.send(Message(
                text="just something",
                timestamp=now(),
                username=username,
            ).to_record())
            while True:
                message = await websocket.recv()
                prompt_text(Message.from_record(message))
            #  async for message in websocket:
            #     await prompt_text(Message.from_record(message))

        # Could be all kinds raised from websockets, but for simplicity we catch all.
        # except Exception:
            # print(f'Could not connect to server at {host}:{port}')
            # return

    asyncio.get_event_loop().run_until_complete(connect_to_server(args.host, args.port))


if __name__ == '__main__':
    main()
