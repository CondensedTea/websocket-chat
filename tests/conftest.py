import fakeredis.aioredis
import pytest
from fakeredis import FakeServer
from fastapi.testclient import TestClient

from app.app import HISTORY_CHANNEL, app, get_redis

server = FakeServer()


async def redis():
    r = await fakeredis.aioredis.create_redis_pool(server=server)
    return r


app.dependency_overrides[get_redis] = redis


@pytest.fixture()
def client():
    c = TestClient(app)
    return c


@pytest.fixture(name='test_redis')
async def fixture_test_redis():
    r = await redis()
    yield r
    await r.flushall()
    r.close()
    await r.wait_closed()


@pytest.fixture()
async def post_message_redis(test_redis):
    text = 'test: It is old message'
    await test_redis.rpush(HISTORY_CHANNEL, text)
    return text
