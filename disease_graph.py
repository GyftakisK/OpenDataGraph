#!/usr/bin/env python


import configparser
import argparse
import datetime
import multiprocessing
import pymongo
import os
import logging
from Harvesters.biomedical_harvesters import HarvestEntrezWrapper, HarvestOBOWrapper, HarvestDrugBankWrapper
from medknow.tasks import taskCoordinator
from medknow.config import settings


class DiseaseGraph:
    def __init__(self, settings_file="config.ini"):
        config = self._read_config(settings_file)
        self._mongodb_host = config["mongoDB"]["host"]
        self._mongodb_port = int(config["mongoDB"]["port"])
        self._mongodb_db_name = config["mongoDB"]["db_name"]
        self._temp_dir = config["filesystem"]["temp_dir"]
        self._semrep_bin_dir = config["filesystem"]["semrep_bin_dir"]
        self._neo4j_host = config["neo4j"]["host"]
        self._neo4j_port = config["neo4j"]["port"]
        self._neo4j_user = config["neo4j"]["user"]
        self._neo4j_pass = config["neo4j"]["password"]
        self._umls_api_key = config["apis"]["umls"]
        self._mongo_client = None
        self._mongodb_inst = None

    def setup(self):
        self._mongo_client = pymongo.MongoClient(self._mongodb_host, self._mongodb_port)
        self._mongodb_inst = self._mongo_client[self._mongodb_db_name]
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s - %(message)s",
                            handlers=[logging.FileHandler(os.path.join(self._temp_dir, "temp.log")),
                                      logging.StreamHandler()])

    @staticmethod
    def _read_config(settings_file):
        config = configparser.ConfigParser()
        with open(settings_file, 'r') as f:
            config.read_file(f)
        return config

    @staticmethod
    def _get_num_of_cores():
        """
        Get number of available cpu cores (leave one core for other jobs)
        :return: number of available cpu cores
        """
        available_cpus = multiprocessing.cpu_count()
        if available_cpus > 2:
            available_cpus -= 1
        return available_cpus

    def _update_job_metadata(self, job_name):
        if self._mongodb_inst['metadata'].find_one({"job": job_name}):
            self._mongodb_inst['metadata'].find_and_modify(query={"job": job_name},
                                                           update={"$set": {'lastUpdate': datetime.datetime.now()}})
        else:
            self._mongodb_inst['metadata'].insert_one({"job": job_name, "lastUpdate": datetime.datetime.now()})

    def _rename_collection(self, old_name, new_name):
        """
        Rename mongoDb collection
        :param old_name: Old name of collection
        :param new_name: New name of collection
        :return:
        """
        self._mongodb_inst[old_name].rename(new_name)

    @staticmethod
    def _get_version():
        """
        Get data version (currently harvesting date)
        :return: string representing data version
        """
        return datetime.datetime.now().strftime("%Y_%m_%d")

    def _set_basic_medknow_settings(self):
        # PIPELINE
        settings['pipeline']['in']['source'] = "mongo"
        settings['pipeline']['in']['type'] = None
        settings['pipeline']['in']['stream'] = False
        settings['pipeline']['in']['parallel'] = True
        settings['pipeline']['trans']['metamap'] = False
        settings['pipeline']['trans']['reverb'] = False
        settings['pipeline']['trans']['semrep'] = False
        settings['pipeline']['trans']['get_concepts_from_edges'] = False
        settings['pipeline']['out']['json'] = False
        settings['pipeline']['out']['csv'] = False
        settings['pipeline']['out']['neo4j'] = True
        settings['pipeline']['out']['mongo_sentences'] = False
        settings['pipeline']['out']['mongo'] = False

        # INPUT
        settings['load']['path']['semrep'] = self._semrep_bin_dir
        settings['load']['mongo']['uri'] = "mongodb://{host}:{port}".format(host=self._mongodb_host,
                                                                            port=self._mongodb_port)
        settings['load']['mongo']['db'] = self._mongodb_db_name
        settings['load']['mongo']['collection'] = None
        settings['load']['mongo']['cache_collection'] = "cache"
        settings['load']['mongo']['file_path'] = None
        settings['load']['text']['itemfield'] = None
        settings['load']['text']['textfield'] = None
        settings['load']['text']['idfield'] = None
        settings['load']['text']['labelfield'] = None
        settings['load']['text']['sent_prefix'] = None
        settings['load']['edges']['itemfield'] = None
        settings['load']['edges']['sub_type'] = None
        settings['load']['edges']['obj_type'] = None
        settings['load']['edges']['sub_source'] = None
        settings['load']['edges']['obj_source'] = None

        # API KEYS
        settings['apis']['umls'] = self._umls_api_key

        # NEO4J
        settings['neo4j']['host'] = self._neo4j_host
        settings['neo4j']['port'] = self._neo4j_port
        settings['neo4j']['user'] = self._neo4j_user
        settings['neo4j']['password'] = self._neo4j_pass
        settings['neo4j']['resource'] = None

        # LOG
        settings['log_path'] = os.path.join(self._temp_dir, "medknow.log")

        # PARALLEL
        settings["num_cores"] = self._get_num_of_cores()
        settings["batch_per_core"] = 100

        # OUTPUT
        settings["out"]["json"]["out_path"] = None
        settings["out"]["json"]["itemfield"] = None
        settings["out"]["json"]["json_doc_field"] = None
        settings["out"]["json"]["json_text_field"] = None
        settings["out"]["json"]["json_id_field"] = None
        settings["out"]["json"]["json_label_field"] = None
        settings["out"]["neo4j"]["out_path"] = "{host}:{port}".format(host=self._neo4j_host,
                                                                      port=self._neo4j_port)

    def update_drugbank(self, path_to_file):
        version = self._get_version()
        job_name = "drugbank_{}".format(version)
        harvester = HarvestDrugBankWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name,
                                           job_name)
        harvester.run()
        self._update_job_metadata(job_name)

    def update_obo(self, path_to_file, obo_type):
        version = self._get_version()
        harvester = HarvestOBOWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        job_name = "{name}_obo_{version}".format(name=harvester.input_obo_name, version=version)
        self._rename_collection(harvester.input_obo_name, job_name)
        self._update_job_metadata(job_name)
        self._set_basic_medknow_settings()
        settings["pipeline"]["in"]["type"] = "edges"
        settings["pipeline"]["trans"]["get_concepts_from_edges"] = True
        settings["load"]["mongo"]["collection"] = job_name
        settings["load"]["mongo"]["file_path"] = "mongodb://{host}:{port}/{db}|{collection}".format(
            host=self._mongodb_host,
            port=self._mongodb_port,
            db=self._mongodb_db_name,
            collection=job_name)
        if obo_type == "DO":
            settings["load"]["edges"]["itemfield"] = obo_type
            settings["load"]["edges"]["sub_type"] = "Entity"
            settings["load"]["edges"]["obj_type"] = "Entity"
            settings["load"]["edges"]["sub_source"] = "UMLS"
            settings["load"]["edges"]["obj_source"] = "UMLS"
            settings["neo4j"]["resource"] = job_name
            settings["out"]["json"]["itemfield"] = obo_type
        elif obo_type == "GO":
            settings["load"]["edges"]["itemfield"] = obo_type
            settings["load"]["edges"]["sub_type"] = "Entity"
            settings["load"]["edges"]["obj_type"] = "Entity"
            settings["load"]["edges"]["sub_source"] = "GO"
            settings["load"]["edges"]["obj_source"] = "GO"
            settings["neo4j"]["resource"] = job_name
            settings["out"]["json"]["itemfield"] = obo_type
        task_manager = taskCoordinator()
        task_manager.print_pipeline()
        task_manager.run()

    def update_disease(self, mesh_term):
        dataset_id = ''.join([word[0].upper() for word in mesh_term.split()])
        job_name = "{}_entrez".format(dataset_id)
        entry = self._mongodb_inst['metadata'].find_one({"job": job_name})
        if entry:
            last_update = entry["lastUpdate"]
        else:
            last_update = datetime.date(1900, 1, 1)
        harvester = HarvestEntrezWrapper(dataset_id, mesh_term, self._temp_dir, last_update, self._mongodb_host,
                                         self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        for suffix in ["pmc", "pubmed", "pubmed_MeSH"]:
            current_name = "{dataset_id}_{suffix}".format(dataset_id=dataset_id, suffix=suffix)
            new_name = "{cur_name}_{cur_date}-{last_update}".format(cur_name=current_name,
                                                                    cur_date=datetime.datetime.now().strftime(
                                                                        "%Y_%m_%d"),
                                                                    last_update=last_update)
            self._rename_collection(current_name, new_name)
        self._update_job_metadata(job_name)

    def cleanup(self):
        self._mongo_client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest_literature", metavar='mesh_term',
                        help="Retrieve online articles relevant to a MeSH term from PubMed and PMC")
    parser.add_argument("--harvest_obo", metavar='path_to_obo',
                        help="Process the OBO file of biomedical ontologies")
    parser.add_argument("--harvest_drugbank", metavar='path_to_xml',
                        help="Process the XML file of DrugBank")
    args = parser.parse_args()

    disease_graph = DiseaseGraph()

    try:
        disease_graph.setup()
        if args.harvest_obo:
            disease_graph.update_obo(args.harvest_obo, "GO")
        if args.harvest_drugbank:
            disease_graph.update_drugbank(args.harvest_drugbank)
        if args.harvest_literature:
            disease_graph.update_disease(args.harvest_literature)
    finally:
        disease_graph.cleanup()


if __name__ == "__main__":
    main()
