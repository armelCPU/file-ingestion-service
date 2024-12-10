from redis.client import Redis

from memory import Memory
from settings import settings

memory = Memory.getInstance()


memory.redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
