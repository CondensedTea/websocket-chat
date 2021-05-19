import pytest

from .conftest import HISTORY_CHANNEL


def test_websocket_recieve(client):
    with client.websocket_connect('/ws/test_user') as websocket:
        data = websocket.receive_text()
    assert data == 'Welcome to chat, test_user'


def test_chat_history_after_connection(client, post_message_redis):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'messages': [post_message_redis]}


@pytest.mark.asyncio
async def test_websocket_send(client, test_redis):
    name = 'test_user'
    message = 'hello world'
    signed_message = f'{name}: {message}'
    with client.websocket_connect(f'/ws/{name}') as websocket:
        websocket.send_text(message)
    [message_from_redis] = await test_redis.lrange(HISTORY_CHANNEL, 0, 1)
    assert signed_message == message_from_redis.decode('utf-8')


def test_disconnect_message(client):
    data = []
    with client.websocket_connect('/ws/main_user') as websocket_primary:
        with client.websocket_connect('/ws/dummy') as websocket_secondary:
            websocket_secondary.close(code=1000)
        for _ in range(2):
            data.append(websocket_primary.receive_text())
    assert data == ['Welcome to chat, main_user', 'dummy left the chat']


def test_name_already_taken(client):
    with client.websocket_connect('/ws/main_user'):
        with client.websocket_connect('/ws/main_user') as websocket_secondary:
            data = websocket_secondary.receive_text()
    assert data == '[Error]: Name already taken, please reconnect with different name'
