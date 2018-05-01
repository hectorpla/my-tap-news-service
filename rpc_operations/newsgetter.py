import pymongo
import pickle
import json
import datetime
from bson import json_util

NEWS_BATCH_SIZE = 5
MAX_PROVIDE_SIZE = 100
CACHE_EXPIRE_TIME_IN_SECONDS = 2 * 60

class NewsRequestMoreThanExpectedError(Exception):
    def __init__(self, to_index):
        self.to_index = to_index

    def __str__(self):
        return '{} greater than {}'.format(self.to_index, MAX_PROVIDE_SIZE - 1)

def _get_recommended_cat_list(pref_model):
    def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
        # from PEP 485
        return abs(a-b) <= max( rel_tol * max(abs(a), abs(b)), abs_tol )

    recommended_categories = []
    if 'userId' in pref_model:
        del pref_model['userId']
    if '_id' in pref_model:
        del pref_model['_id']
    pref_list = sorted(pref_model.items(), key=lambda pair: pair[1], reverse=True)
    print('newsgetter:', pref_list)

    highest = pref_list[0][1]
    for cat, pref in pref_list:
        if isclose(pref, highest):
            recommended_categories.append(cat)
    
    return recommended_categories if len(recommended_categories) < len(pref_list) else []

def get_news_for_user(news_collection, pref_collection, 
                      redis_client, user_id, page_num):
    from_index = page_num * NEWS_BATCH_SIZE
    to_index = (page_num + 1) * NEWS_BATCH_SIZE

    if to_index >= MAX_PROVIDE_SIZE:
        raise NewsRequestMoreThanExpectedError(to_index)
        # TODO consider silent it and handle

    
    news_in_page = None

    news_digest_list_digest = redis_client.get(user_id)

    if not news_digest_list_digest:
        # TODO: customize the list for different user
        total_news = (news_collection.find()
                      .sort([('publishedAt', pymongo.DESCENDING)])
                      .limit(MAX_PROVIDE_SIZE))
        total_news = list(total_news)

        news_digest_list_digest = pickle.dumps([news['digest'] for news in total_news])
        redis_client.set(user_id, news_digest_list_digest)
        redis_client.expire(user_id, CACHE_EXPIRE_TIME_IN_SECONDS)
        news_in_page = total_news[from_index:to_index]
    else:
        news_digest_list = pickle.loads(news_digest_list_digest)
        selected_digests = news_digest_list[from_index:to_index]
        news_in_page = news_collection.find({'digest': {'$in': selected_digests}})
        news_in_page = list(news_in_page)

    # get recommended catergories list
    recommended_categories = []
    if pref_collection:
        pref_model = pref_collection.find_one({'userId': user_id})
        if pref_model:
            recommended_categories = _get_recommended_cat_list(pref_model)
            print('newsgetter: recommended list for user {}: {}'.format(user_id, 
                recommended_categories))

    # augment news
    for news in news_in_page:
        if news['text']:
            del news['text']
        if news['publishedAt'] + datetime.timedelta(hours=12) < datetime.datetime.today():
            news['relativeTime'] = 'New'
        if 'category' in news and news['category'] in recommended_categories:
            news['recommended'] = True

    # print(news_in_page)

    # dumps bson
    result = json.loads(json.dumps(news_in_page, default=json_util.default))
    print(type(result))
    return result
