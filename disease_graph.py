import configparser
import datetime
import pymongo
from Harvesters.biomedical_harvesters import HarvestEntrezWrapper, HarvestOBOWrapper, HarvestDrugBankWrapper


class DiseaseGraph:
    def __init__(self, settings_file="config.ini"):
        config = self._read_config(settings_file)
        self._mongodb_host = config["mongoDB"]["host"]
        self._mongodb_port = int(config["mongoDB"]["port"])
        self._mongodb_db_name = config["mongoDB"]["db_name"]
        self._temp_dir = config["filesystem"]["temp_dir"]
        self._mongo_client = pymongo.MongoClient(self._mongodb_host, self._mongodb_port)
        self._mongodb_inst = self._mongo_client[self._mongodb_db_name]

    @staticmethod
    def _read_config(settings_file):
        config = configparser.ConfigParser()
        with open(settings_file, 'r') as f:
            config.read_file(f)
        return config

    def _update_job_metadata(self, job_name):
        if self._mongodb_inst['metadata'].find_one({"harvester": job_name}):
            self._mongodb_inst['metadata'].find_and_modify(query={"harvester": job_name},
                                                           update={"$set": {'lastUpdate': datetime.datetime.now()}})
        else:
            self._mongodb_inst['metadata'].insert_one({"harvester": job_name, "lastUpdate": datetime.datetime.now()})

    def update_drugbank(self, filename):
        harvester = HarvestDrugBankWrapper(filename, self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        job_name = "drugbank"
        self._update_job_metadata(job_name)

    def update_obo(self, filename):
        harvester = HarvestOBOWrapper(filename, self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        job_name = "{}_obo".format(harvester.input_obo_name)
        self._update_job_metadata(job_name)

    def update_disease(self, dataset_id, mesh_term):
        job_name = "{}_entrez".format(dataset_id)
        entry = self._mongodb_inst['metadata'].find_one({"harvester": job_name})
        if entry:
            last_update = entry["lastUpdate"]
        else:
            last_update = datetime.date(1900, 1, 1)
        harvester = HarvestEntrezWrapper(dataset_id, mesh_term, self._temp_dir, last_update, self._mongodb_host,
                                         self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        self._update_job_metadata(job_name)

    def cleanup(self):
        self._mongo_client.close()
