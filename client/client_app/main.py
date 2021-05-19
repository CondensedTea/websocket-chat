import sys
from pathlib import Path
from threading import Thread

import requests
import typer
import websocket

app = typer.Typer()


def pooling_loop(ws: websocket.WebSocket) -> None:
    try:
        while True:
            msg = ws.recv()
            typer.echo(msg)
    except websocket.WebSocketConnectionClosedException:
        #        typer.echo('[Error]: Name already taken, please reconnect with different name')
        return


@app.command()
def main(
    username: str = typer.Argument(..., help='Your name in chat room'),
    url: str = typer.Option(
        'localhost:8000', help='URL of websocket chat to connect to'
    ),
    history: bool = typer.Option(False, '--history'),
) -> None:
    if history:
        response = requests.get('http://' + url)
        data = response.json()
        for msg in data['messages']:
            typer.echo(msg)
    ws = websocket.WebSocket()
    ws_path = Path(url, 'ws', username)
    ws.connect('ws://' + str(ws_path))
    t = Thread(target=pooling_loop, args=(ws,), daemon=True)
    t.start()
    try:
        while True:
            msg = input()
            ws.send(msg)
    except KeyboardInterrupt:
        print('\nDisconnected from the chat.')
        sys.exit(1)

    except websocket.WebSocketConnectionClosedException:
        sys.exit(1)


if __name__ == '__main__':
    app()
