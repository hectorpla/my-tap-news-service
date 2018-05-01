import sys
import os

# from bson.json_util import loads
import redis
sys.path.append(os.path.join(os.path.dirname(__file__),'..','utils'))
import mongodb_client

from newsgetter import get_news_for_user

DB_NAME = 'demo'
COLLECTION_NAME = 'news'
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'

PREF_DB_NAME = 'pref'
PREF_COLLECTION_NAME = 'test'

news_collection = mongodb_client.get_db(DB_NAME).get_collection(COLLECTION_NAME)
pref_collection = mongodb_client.get_db(PREF_DB_NAME).get_collection(PREF_COLLECTION_NAME)
redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)

def test_basic():
    news_list1 = get_news_for_user(news_collection,
                             pref_collection,
                             redis_client,
                             'test_admin', 0)
    # news_list1 = loads(news_list1)
    print(news_list1)

    news_list2 = get_news_for_user(news_collection,
                                   pref_collection,
                                   redis_client,
                                   'test_admin', 1)
    # news_list2 = loads(news_list2)
    print(news_list2)

    intersection = set(map(str, news_list1)) & set(map(str, news_list2))
    print('\n-------intersect {}, length of {}', intersection, len(intersection))
    assert len(intersection) == 0
    print('test passed')

if __name__ == '__main__':
    test_basic()