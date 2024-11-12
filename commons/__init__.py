from common_schemas.models import IndexedEntities
from common_schemas.utils.index_utils import get_entity_index_name
from common_utils.general import TextPreprocessor
from db_wrapper.elasticsearch import ElasticsearchWrapper
from db_wrapper.mongodb import MongoWrapper
from redis.client import Redis

from memory import Memory
from settings import settings

memory = Memory.getInstance()

memory.es_wrapper = ElasticsearchWrapper(
    es_host=settings.ES_HOST,
    es_port=settings.ES_PORT,
    es_username=settings.ES_USERNAME,
    es_password=settings.ES_PASSWORD,
    es_certificate=settings.ES_CERTIFICATE,
    es_timeout=settings.ES_TIMEOUT,
    es_insert_batch_size=settings.ES_INSERT_BATCH_SIZE,
    es_retrieve_batch_size=settings.ES_RETRIEVE_BATCH_SIZE,
)

memory.mongo_wrapper = MongoWrapper(
    host=settings.MONGO_HOST,
    port=settings.MONGO_PORT,
    username=settings.MONGO_USERNAME,
    password=settings.MONGO_PASSWORD,
    database=settings.MONGO_DATABASE,
)

memory.text_processor = TextPreprocessor()

memory.redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

for entity in IndexedEntities:
    memory.indexes[entity] = get_entity_index_name(entity)
