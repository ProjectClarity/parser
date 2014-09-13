import os
from contextlib import contextmanager

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient(os.environ.get('MONGO_URI'))
db = client[os.environ.get('MONGO_URI').split('/')[-1]]
users = db.users
raw_data = db.raw_data
processed_data = db.processed_data

@contextmanager
def get_raw_email(object_id):
    raw_email = raw_data.find_one({'_id':ObjectId(objectId)})
    if processed_data.find_one({'email_id':raw_email['id']}):
        raise Exception('dupe')
    del raw_email['_id']
    try:
        yield raw_email
        raw_data.remove({'_id':ObjectId(objectId)})
    except Exception as e:
        raise e

def store_processed_data(processed_data_dict):
    processed_data.insert(processed_data_dict)
