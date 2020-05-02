#!/usr/bin/env python


import configparser
import argparse
import datetime
import multiprocessing
import os
import logging
from db_manager.mongodb_manager import MongoDbManager
from harvesters.biomedical_harvesters import HarvestEntrezWrapper, HarvestOBOWrapper, HarvestDrugBankWrapper
from medknow.tasks import taskCoordinator
from medknow.config import settings


DEBUG = True


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
        self._mongodb_manager = None

    def setup(self):
        self._mongodb_manager = MongoDbManager(self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
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
        if self._mongodb_manager.get_entry_from_field('metadata', "job", job_name):
            self._mongodb_manager.update_field('metadata', "job", job_name, 'lastUpdate', datetime.datetime.now())
        else:
            self._mongodb_manager.insert_entry('metadata', {"job": job_name, "lastUpdate": datetime.datetime.now()})

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

    @staticmethod
    def _run_medknow():
        task_manager = taskCoordinator()
        task_manager.print_pipeline()
        task_manager.run()

    def _set_edge_specific_medknow_settings(self, collection, resource, job_type):
        sub_source_from_type = {"DO": "UMLS",
                                "GO": "GO",
                                "MESH": "MSH",
                                "DRUGBANK": "DRUGBANK",
                                "pubmed_MeSH": "TEXT"}
        obj_source_from_type = {"DO": "UMLS",
                                "GO": "GO",
                                "MESH": "MSH",
                                "DRUGBANK": "DRUGBANK",
                                "pubmed_MeSH": "MSH"}
        sub_type_from_type = {"DO": "Entity",
                              "GO": "Entity",
                              "MESH": "Entity",
                              "DRUGBANK": "Entity",
                              "pubmed_MeSH": "Article"}
        obj_type_from_type = {"DO": "Entity",
                              "GO": "Entity",
                              "MESH": "Entity",
                              "DRUGBANK": "Entity",
                              "pubmed_MeSH": "Entity"}
        settings["pipeline"]["in"]["type"] = "edges"
        settings["pipeline"]["trans"]["get_concepts_from_edges"] = True
        settings["load"]["mongo"]["collection"] = collection
        settings["load"]["mongo"]["file_path"] = "mongodb://{host}:{port}/{db}|{collection}".format(
                                                                                            host=self._mongodb_host,
                                                                                            port=self._mongodb_port,
                                                                                            db=self._mongodb_db_name,
                                                                                            collection=collection)
        settings["load"]["edges"]["itemfield"] = job_type
        settings["load"]["edges"]["sub_type"] = sub_type_from_type[job_type]
        settings["load"]["edges"]["obj_type"] = obj_type_from_type[job_type]
        settings["load"]["edges"]["sub_source"] = sub_source_from_type[job_type]
        settings["load"]["edges"]["obj_source"] = obj_source_from_type[job_type]
        settings["neo4j"]["resource"] = resource
        settings["out"]["json"]["itemfield"] = job_type

    def update_drugbank(self, path_to_file):
        version = self._get_version()
        job_name = "drugbank_{}".format(version)
        harvester = HarvestDrugBankWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name,
                                           job_name)
        harvester.run()
        self._update_job_metadata(job_name)
        self._set_basic_medknow_settings()
        self._set_edge_specific_medknow_settings(job_name, job_name, "DRUGBANK")
        self._run_medknow()

    def update_obo(self, path_to_file, obo_type):
        version = self._get_version()
        harvester = HarvestOBOWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        job_name = "{name}_obo_{version}".format(name=harvester.input_obo_name, version=version)
        self._mongodb_manager.rename_collection(harvester.input_obo_name, job_name)
        self._update_job_metadata(job_name)
        self._set_basic_medknow_settings()
        self._set_edge_specific_medknow_settings(job_name, job_name, obo_type)
        self._run_medknow()

    def update_disease(self, mesh_term):
        dataset_id = ''.join([word[0].upper() for word in mesh_term.split()])
        job_name = "{}_entrez".format(dataset_id)
        entry = self._mongodb_manager.get_entry_from_field('metadata', "job", job_name)
        if entry:
            last_update = entry["lastUpdate"]
        else:
            last_update = datetime.date(2020, 4, 24)
        harvester = HarvestEntrezWrapper(dataset_id, mesh_term, self._temp_dir, last_update, self._mongodb_host,
                                         self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        collections = dict()
        for suffix in ["pmc", "pubmed", "pubmed_MeSH"]:
            current_name = "{dataset_id}_{suffix}".format(dataset_id=dataset_id, suffix=suffix)
            new_name = "{cur_name}_{cur_date}_{last_update}".format(cur_name=current_name,
                                                                    cur_date=datetime.datetime.now().strftime(
                                                                        "%Y_%m_%d"),
                                                                    last_update=last_update.strftime(
                                                                        "%Y_%m_%d"))
            if self._mongodb_manager.collection_exists(current_name):
                self._mongodb_manager.rename_collection(current_name, new_name)
                if DEBUG:
                    self._mongodb_manager.prune_collection(new_name)
            collections[suffix] = new_name
        # self._update_job_metadata(job_name)

        for collection_type in collections.keys():
            self._set_basic_medknow_settings()
            if collection_type == "pubmed_MeSH":
                self._set_edge_specific_medknow_settings(collections[collection_type],
                                                         job_name, "pubmed_MeSH")

                self._run_medknow()

    def cleanup(self):
        self._mongodb_manager.on_exit()


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
            disease_graph.update_obo(args.harvest_obo, "MESH")
        if args.harvest_drugbank:
            disease_graph.update_drugbank(args.harvest_drugbank)
        if args.harvest_literature:
            disease_graph.update_disease(args.harvest_literature)
    finally:
        disease_graph.cleanup()


if __name__ == "__main__":
    main()
