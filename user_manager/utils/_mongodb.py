from pymongo.collection import Collection

from novousers.settings import mongo_db


def insert_document(collection_name, new_document):
    collection: Collection = mongo_db[collection_name]
    collection.insert_one(new_document)


def get_documents(collection_name, filter_object):
    collection: Collection = mongo_db[collection_name]
    return collection.find(filter_object)
