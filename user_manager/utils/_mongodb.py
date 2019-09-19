from datetime import datetime
from json import JSONEncoder

from bson import ObjectId
from pymongo.collection import Collection

from novousers.settings import mongo_db


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return o.replace(microsecond=0).isoformat()
        return JSONEncoder.default(self, o)


def insert_document(collection_name, new_document):
    collection: Collection = mongo_db[collection_name]
    collection.insert_one(new_document)


def get_documents(collection_name, filter_object, projection_object):
    collection: Collection = mongo_db[collection_name]
    return [d for d in collection.find(filter_object, projection_object)]
