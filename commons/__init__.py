from common_schemas.models import IndexedEntities
from common_schemas.utils.index_utils import get_entity_index_name
from common_utils.general import TextPreprocessor
from db_wrapper.elasticsearch import ElasticsearchWrapper
from db_wrapper.mongodb import MongoWrapper
from redis.client import Redis

from memory import Memory
from settings import settings

memory = Memory.getInstance()


memory.mongo_wrapper = MongoWrapper(
    host=settings.MONGO_HOST,
    port=settings.MONGO_PORT,
    username=settings.MONGO_USERNAME,
    password=settings.MONGO_PASSWORD,
    database=settings.MONGO_DATABASE,
)


memory.redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


