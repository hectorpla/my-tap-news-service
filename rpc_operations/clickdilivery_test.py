import os, sys

import clickdilivery

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from config_reader import get_config
from cloud_amqp_client import AMQPClient

config = get_config(os.path.join(os.path.dirname(__file__),
                                 '..', 'config', 'config.json'))

USER_CLICK_QUEUE_URL = config['new_click_queue_url']
USER_CLICK_QUEUE_NAME = 'test'

def test_basic():
    queue_client = AMQPClient(USER_CLICK_QUEUE_URL, USER_CLICK_QUEUE_NAME)

    user_id, digest = 'click tester', 'digest'
    clickdilivery.send_click(queue_client, user_id, digest)

    message = queue_client.get_message()

    print(message)
    assert message['userId'] == user_id
    assert message['newsDigest'] == digest

    queue_client.close()
    print('click test passed')


if __name__ == '__main__':
    test_basic()