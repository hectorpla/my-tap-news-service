import datetime

def send_click(click_queue_client, user_id, news_digest):
    if not click_queue_client.is_connected():
        click_queue_client.connect()

    print('Click log: queue info', click_queue_client)

    click_queue_client.send_message({
        'userId': user_id,
        'newsDigest': news_digest,
        'timeStamp': str(datetime.datetime.utcnow())
    })