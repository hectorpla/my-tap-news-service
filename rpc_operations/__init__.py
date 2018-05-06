import sys
import os

import redis
sys.path.append(os.path.join(os.path.dirname(__file__),'..','utils'))
import mongodb_client
from config_reader import get_config
from cloud_amqp_client import AMQPClient

# TODO makes server.py work, but not certain if it is a good practice
sys.path.append(os.path.join(os.path.dirname(__file__)))
from newsgetter import get_news_for_user
from clickdilivery import send_click

# TODO should make a more reliable way to find the config file
# config = get_config(os.path.join(os.path.dirname(__file__),
#                                  '..', 'config', 'config.json'))

# override the config data structure with env vars
config = os.environ

NEWS_DB_NAME = config['news_db']
NEWS_COLLECTION_NAME = config['new_collection']

# TODO for test, change db name and collection name for real product
# NEWS_DB_NAME = 'demo' 
# NEWS_COLLECTION_NAME = 'news'

PREF_DB_NAME = config['preference_db']
PREF_COLLECTION_NAME = config['preference_collection']

REDIS_HOST = config.get('redis_host')
REDIS_PORT = config.get('redis_port')

USER_CLICK_QUEUE_URL = config['new_click_queue_url']
USER_CLICK_QUEUE_NAME = config['new_click_queue_name']


# TODO should do init here? or let the sub-module take care of them
news_collection = mongodb_client.get_db(NEWS_DB_NAME).get_collection(NEWS_COLLECTION_NAME)
pref_collection = mongodb_client.get_db(PREF_DB_NAME).get_collection(PREF_COLLECTION_NAME)

if REDIS_HOST:
    REDIS_URL = REDIS_HOST + ":" + (REDIS_PORT if REDIS_PORT else '')
else:
    REDIS_URL = os.environ.get("REDIS_URL") # heroku specific
redis_client = redis.from_url(REDIS_URL)

click_queue_client = AMQPClient(USER_CLICK_QUEUE_URL, USER_CLICK_QUEUE_NAME)


__all__ = ['get_news', 'log_click']

# for test, maybe bad
def init():
    global click_queue_client
    click_queue_client = AMQPClient(USER_CLICK_QUEUE_URL, USER_CLICK_QUEUE_NAME)

def get_news(user_id, page_num):
    print('++ RPC server: get news for {}, page #{}'.format(user_id, page_num))
    return get_news_for_user(news_collection,
                             pref_collection,
                             redis_client,
                             user_id, page_num)

def log_click(user_id, news_digest):
    print('++ RPC server: user {} clicked news {}'.format(user_id, news_digest))
    send_click(click_queue_client, user_id, news_digest)
