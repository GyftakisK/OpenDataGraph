import pymongo


class MongoDbManager:
    def __init__(self, host, port, db_name):
        self._mongo_client = pymongo.MongoClient(host, port)
        self._mongodb_inst = self._mongo_client[db_name]

    def rename_collection(self, old_name, new_name):
        """
        Rename mongoDb collection
        :param old_name: Old name of collection
        :param new_name: New name of collection
        :return:
        """
        self._mongodb_inst[old_name].rename(new_name)

    def prune_collection(self, collection, count_after_prune):
        documents = self._mongodb_inst[collection].find()
        delete_docs = documents[count_after_prune:]
        for document in delete_docs:
            self._mongodb_inst[collection].delete_one({"_id": document["_id"]})

    def collection_exists(self, collection):
        return collection in self._mongodb_inst.collection_names()

    def get_entry_from_field(self, collection, field_name, field_value):
        return self._mongodb_inst[collection].find_one({field_name: field_value})

    def delete_entry_from_field(self, collection, key_name, key_value):
        self._mongodb_inst[collection].delete_many({key_name: key_value})

    def insert_entry(self, collection, entry):
        self._mongodb_inst[collection].insert_one(entry)

    def update_field(self, collection, key_name, key_value, field_name, new_value):
        self._mongodb_inst[collection].find_and_modify(query={key_name: key_value},
                                                       update={"$set": {field_name: new_value}})

    def get_distinct_field_values(self, collection, field_name):
        return self._mongodb_inst[collection].distinct(field_name)

    def on_exit(self):
        self._mongo_client.close()
