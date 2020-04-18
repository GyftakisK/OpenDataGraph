import configparser
import pymongo


class DiseaseGraph:
    def __init__(self, settings_file="config.ini"):
        config = self._read_config(settings_file)
        self._mongodb_host = config["mongoDB"]["host"]
        self._mongodb_port = int(config["mongoDB"]["port"])
        self._mongodb_db_name = config["mongoDB"]["db_name"]
        self._mongo_client = pymongo.MongoClient(self._mongodb_host, self._mongodb_port)
        self._mongodb_inst = self._mongo_client[self._mongodb_db_name]

    @staticmethod
    def _read_config(settings_file):
        config = configparser.ConfigParser()
        with open(settings_file, 'r') as f:
            config.read_file(f)
        return config

    def update_drugbank(self, filename):
        pass

    def update_obo(self, filename):
        pass

    def update_disease(self, mesh_term):
        pass

    def cleanup(self):
        self._mongo_client.close()
