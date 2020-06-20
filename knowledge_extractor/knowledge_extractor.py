import configparser
import datetime
import logging
import multiprocessing
import os

from db_manager.mongodb_manager import MongoDbManager
from harvesters.biomedical_harvesters import HarvestDrugBankWrapper, HarvestOBOWrapper, HarvestEntrezWrapper
from medknow.config import settings
from medknow.tasks import taskCoordinator
from utilities import get_filename_from_file_path, NotSupportedOboFile, DiseaseAlreadyInGraph, NoDiseasesInGraph
from typing import List, Dict
DEBUG = False 


class KnowledgeExtractor:
    def __init__(self):
        self._mongodb_host = None
        self._mongodb_port = None
        self._mongodb_db_name = None
        self._temp_dir = None
        self._semrep_bin_dir = None
        self._neo4j_host = None
        self._neo4j_port = None
        self._neo4j_user = None
        self._neo4j_pass = None
        self._umls_api_key = None
        self._mongodb_manager = None
        self._supported_obo_types = ['DO', 'GO', 'MeSH']
        self._literature_harvester_sources = ("pmc", "pubmed", "pubmed_MeSH")
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s - %(message)s",
                            handlers=[logging.StreamHandler()])

    def setup(self):
        """
        Method to setup basic functionality.
        Must be called before any other functions
        """
        self._mongodb_host = os.environ.get('MONGODB_HOST')
        self._mongodb_port = int(os.environ.get('MONGODB_PORT'))
        self._mongodb_db_name = os.environ.get('MONGODB_NAME')
        self._temp_dir = os.environ.get('UPLOAD_FOLDER')
        self._semrep_bin_dir = os.environ.get('SEMREP_BIN_DIR')
        self._neo4j_host = os.environ.get('NEO4J_HOST')
        self._neo4j_port = os.environ.get('NEO4J_PORT')
        self._neo4j_user = os.environ.get('NEO4J_USER')
        self._neo4j_pass = os.environ.get('NEO4J_PASS')
        self._umls_api_key = os.environ.get('UMLS_API_KEY')
        self._mongodb_manager = MongoDbManager(self._mongodb_host, self._mongodb_port, self._mongodb_db_name)

    def update_drugbank(self, path_to_file: str, version: str = None):
        """
        Method to harvest drugbank XML file and insert relations to graph
        :param path_to_file: Path to XML
        :param version: The version of the XML file
        """
        if not version:
            version = self._get_version()
        job_name = "DRUGBANK_{}".format(version)
        harvester = HarvestDrugBankWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name,
                                           job_name)
        harvester.run()
        self._set_basic_medknow_settings()
        self._set_edge_specific_medknow_settings(job_name, job_name, "DRUGBANK")
        self._run_medknow()
        metadata_input = {'filename': get_filename_from_file_path(path_to_file), "type": "DRUGBANK", "version": version}
        self._update_job_metadata(job_name, metadata_input)

    def update_obo(self, path_to_file: str, obo_type: str, version: str = None):
        """
        Method to harvest ontology files and insert relations to graph
        :param path_to_file: Path to OBO file
        :param obo_type: Type of OBO file. Supported types: [GO, DO, MeSH]
        :param version: The version of the OBO file
        """
        if obo_type not in self._supported_obo_types:
            raise NotSupportedOboFile(obo_type)
        if not version:
            version = self._get_version()
        harvester = HarvestOBOWrapper(path_to_file, self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        job_name = "{obo_type}_{version}".format(obo_type=obo_type, version=version)
        self._mongodb_manager.rename_collection(harvester.input_obo_name, job_name)
        self._set_basic_medknow_settings()
        self._set_edge_specific_medknow_settings(job_name, job_name, obo_type)
        self._run_medknow()
        metadata_input = {'filename': get_filename_from_file_path(path_to_file), "type": obo_type, "version": version}
        self._update_job_metadata(job_name, metadata_input)

    def add_disease(self, mesh_term: str):
        """
        Method to harvest literature concerning a disease from provided MeSH term,
        extract relations from text and insert them to graph
        :param mesh_term: Disease MeSH term
        """
        job_name = "disease_literature"
        entry = self._mongodb_manager.get_entry_from_field('metadata', "job", job_name)
        if entry:
            mesh_terms = entry["input"]
            if mesh_term in mesh_terms:
                raise DiseaseAlreadyInGraph("MeSH TERM: {} already in DB".format(mesh_term))
            mesh_terms.append(mesh_term)
            date_to = entry["lastUpdate"]
        else:
            mesh_terms = [mesh_term]
            date_to = datetime.datetime.utcnow()
        date_from = datetime.date(1900, 1, 1)
        self._update_literature(self._get_dataset_id_from_mesh_term(mesh_term),
                                date_from, date_to, job_name, mesh_terms, mesh_term)

    def update_diseases(self):
        """
        Method to update literature concerning diseases already available in the graph
        """
        job_name = "disease_literature"
        entry = self._mongodb_manager.get_entry_from_field('metadata', "job", job_name)
        if entry:
            mesh_terms = entry["input"]
            date_from = entry["lastUpdate"]
        else:
            raise NoDiseasesInGraph()
        date_to = datetime.datetime.utcnow()
        self._update_literature("update", date_from, date_to, job_name, mesh_terms, mesh_terms)

    def cleanup(self):
        """
        Method to be called before exit
        """
        self._mongodb_manager.on_exit()

    def get_literature_status(self) -> dict:
        """
        Method to retrieve metadata for literature harvesting
        :return: Dictionary containing MeSH terms and last update timestamp
        """
        job_name = "disease_literature"
        entry = self._mongodb_manager.get_entry_from_field('metadata', "job", job_name)
        if entry:
            return {"mesh_terms": entry["input"], "last_update": entry["lastUpdate"]}
        else:
            return {"mesh_terms": [], "last_update": None}

    def get_structured_resources_jobs_status(self) -> List[Dict]:
        """
        Method to retrieve metadata for structured (OBO, DRUGBANK) harvesting
        :return: List of dictionaries containing filenames and timestamps
        """
        return [{"filename": entry["input"]["filename"],
                 "type": entry["input"]["type"],
                 "version": entry["input"]["version"],
                 "last_update": entry["lastUpdate"]}
                for entry in self._mongodb_manager.get_all_entries('metadata')
                if entry['job'] != "disease_literature"]

    def print_job_status(self):
        """
        Method to print a job status report
        """
        print("STATUS")
        print("=" * 50)
        literature = self.get_literature_status()
        print("MeSH Terms Harvested: {}".format(literature["mesh_terms"]))
        print("Last Update: {}".format(literature["last_update"]))
        print("-" * 50)
        for structured in self.get_structured_resources_jobs_status():
            print("Filename: {}".format(structured["filename"]))
            print("Last Update: {}".format(structured["last_update"]))
            print("-" * 50)

    @staticmethod
    def _get_num_of_cores() -> int:
        """
        Get number of available cpu cores (leave one core for other jobs)
        :return: number of available cpu cores
        """
        available_cpus = multiprocessing.cpu_count()
        if available_cpus > 2:
            available_cpus -= 1
        return available_cpus

    def _update_job_metadata(self, job_name: str, input_,
                             last_update=datetime.datetime.utcnow()):
        """
        Method to update job metadata in mongoDb
        :param job_name: The name of the job for which we want to write metadata
        :param input_: The input of the job
        :param last_update: Timestamp of the last update
        """
        if self._mongodb_manager.get_entry_from_field('metadata', "job", job_name):
            self._mongodb_manager.update_field('metadata', "job", job_name, 'lastUpdate', last_update)
            self._mongodb_manager.update_field('metadata', "job", job_name, 'input', input_)
        else:
            self._mongodb_manager.insert_entry('metadata', {"job": job_name, 'input': input_,
                                                            "lastUpdate": last_update})

    def _update_pmids(self, source, pmids):
        entry = self._mongodb_manager.get_entry_from_field('pmid_cache', "source", source)
        if entry:
            self._mongodb_manager.update_field('pmid_cache', "source", source, 'pmids',
                                               entry['pmids'] + pmids)
        else:
            self._mongodb_manager.insert_entry('pmid_cache', {"source": source, 'pmids': pmids})

    def _get_pmids_from_collection(self, collection: str) -> list:
        """
        Helper method to get all unique pmid in an article mongoDb collection
        :param collection: Name of the collection
        :return: List of pmids
        """
        return self._mongodb_manager.get_distinct_field_values(collection, "pmid")

    @staticmethod
    def _get_version() -> str:
        """
        Get data version (currently harvesting date)
        :return: string representing data version
        """
        return datetime.datetime.utcnow().strftime("%Y_%m_%d")

    def _set_basic_medknow_settings(self):
        """
        Method to set basic common settings for Medknow, needed for all jobs
        """
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

    def _set_edge_specific_medknow_settings(self, collection: str, resource: str, job_type: str):
        """
        Method to set settings for Medknow, needed for edge insertion jobs
        """
        settings_from_type = {"DO": {"sub": {"source": "UMLS", "type": "Entity"},
                                     "obj": {"source": "UMLS", "type": "Entity"}},
                              "GO": {"sub": {"source": "GO", "type": "Entity"},
                                     "obj": {"source": "GO", "type": "Entity"}},
                              "MeSH": {"sub": {"source": "MSH", "type": "Entity"},
                                       "obj": {"source": "MSH", "type": "Entity"}},
                              "DRUGBANK": {"sub": {"source": "DRUGBANK", "type": "Entity"},
                                           "obj": {"source": "DRUGBANK", "type": "Entity"}},
                              "pubmed_MeSH": {"sub": {"source": "TEXT", "type": "Article"},
                                              "obj": {"source": "MSH", "type": "Entity"}},
                              }
        settings["pipeline"]["in"]["type"] = "edges"
        settings["pipeline"]["trans"]["get_concepts_from_edges"] = True
        settings["load"]["mongo"]["collection"] = collection
        settings["load"]["mongo"]["file_path"] = "mongodb://{host}:{port}/{db}|{collection}".format(
                                                                                            host=self._mongodb_host,
                                                                                            port=self._mongodb_port,
                                                                                            db=self._mongodb_db_name,
                                                                                            collection=collection)
        settings["load"]["edges"]["itemfield"] = job_type
        settings["load"]["edges"]["sub_type"] = settings_from_type[job_type]["sub"]["type"]
        settings["load"]["edges"]["obj_type"] = settings_from_type[job_type]["obj"]["type"]
        settings["load"]["edges"]["sub_source"] = settings_from_type[job_type]["sub"]["source"]
        settings["load"]["edges"]["obj_source"] = settings_from_type[job_type]["obj"]["source"]
        settings["neo4j"]["resource"] = resource
        settings["out"]["json"]["itemfield"] = job_type

    def _set_pubmed_medknow_settings(self, collection: str, resource: str, collection_type: str):
        """
        Method to set settings for Medknow, needed for literature (PubMed) relations extraction
        :param collection: Name of the mongo collection to be used as input
        :param resource: Name of the resource field of edges, used for data provenance
        :param collection_type: Type of the collection being processed. Supported values ["pubmed", "pmc"]
        """
        settings["pipeline"]["in"]["type"] = "text"
        settings["pipeline"]["trans"]["semrep"] = True
        settings["load"]["mongo"]["collection"] = collection
        settings["load"]["mongo"]["file_path"] = "mongodb://{host}:{port}/{db}|{collection}".format(
            host=self._mongodb_host,
            port=self._mongodb_port,
            db=self._mongodb_db_name,
            collection=collection)
        settings["load"]["text"]["itemfield"] = collection
        settings["load"]["text"]["textfield"] = "abstractText" if collection_type == "pubmed" else "body_Filtered"
        settings["load"]["text"]["idfield"] = "pmid"
        settings["load"]["text"]["labelfield"] = "title"
        settings["load"]["text"]["sent_prefix"] = "abstract" if collection_type == "pubmed" else "fullText"
        settings["neo4j"]["resource"] = "{}_{}".format(resource, collection_type)
        settings["out"]["json"]["itemfield"] = collection
        settings["out"]["json"]["json_doc_field"] = "abstractText" if collection_type == "pubmed" else "body_Filtered"
        settings["out"]["json"]["json_text_field"] = "text"
        settings["out"]["json"]["json_id_field"] = "id"
        settings["out"]["json"]["json_label_field"] = "title"

    @staticmethod
    def _run_medknow():
        """
        Helper method to run Medknow
        """
        task_manager = taskCoordinator()
        task_manager.print_pipeline()
        task_manager.run()

    def _get_harvested_pubmed_collections(self, dataset_id: str, date_to: datetime.datetime,
                                          date_from: datetime.datetime) -> dict:
        """
        Helper method to get created collections in mongoDb as a result of literature harvesting
        :param dataset_id: Dataset ID provided to harvester
        :param date_to: Timestamp denoting the ending completion date of articles
        :param date_from: Timestamp denoting the starting completion date of articles
        :return: Available collections per source
        """
        collections = dict()
        for suffix in self._literature_harvester_sources:
            collection = "{dataset_id}_{date_to}_{date_from}_{suffix}".format(dataset_id=dataset_id,
                                                                              date_to=date_to.strftime("%Y_%m_%d"),
                                                                              date_from=date_from.strftime("%Y_%m_%d"),
                                                                              suffix=suffix)

            if self._mongodb_manager.collection_exists(collection):
                collections[suffix] = collection
        return collections

    def _remove_already_harvested_pubmed_articles(self, available_collections_per_source: dict) -> dict:
        """
        Helper method to remove articles that are already present in the graph
        :param available_collections_per_source:
        :return: New article pmids harvested per source
        """
        pmids = dict()
        for source in ["pmc", "pubmed"]:
            if source not in available_collections_per_source:
                continue
            pmids[source] = self._get_pmids_from_collection(available_collections_per_source[source])
            entry = self._mongodb_manager.get_entry_from_field('pmid_cache', "source", source)

            if not entry:
                continue

            common_pmids = set(entry["pmids"]) & set(pmids[source])
            for pmid in common_pmids:
                self._mongodb_manager.delete_entry_from_field(available_collections_per_source[source],
                                                              "pmid", pmid)
                self._mongodb_manager.delete_entry_from_field(available_collections_per_source["pubmed_MeSH"],
                                                              "s", pmid)
                pmids[source].remove(pmid)
                logging.debug("Removing already harvested article with pmid={}".format(pmid))
        return pmids

    @staticmethod
    def _get_dataset_id_from_mesh_term(mesh_term: str) -> str:
        """
        Helper method to create dataset ID from provided MeSH term
        :param mesh_term:
        :return: Words contained in MeSH term divided with underscores
        """
        dataset_id = "_".join(mesh_term.replace(",", "").replace("-", "_").split())
        return dataset_id.lower()

    def _update_literature(self, dataset_id, date_from, date_to, job_name, mesh_terms, terms_to_harvest):
        """
        Helper method to harvest literature and update graph
        :param dataset_id: Dataset ID provided to harvester
        :param date_to: Timestamp denoting the ending completion date of articles
        :param date_from: Timestamp denoting the starting completion date of articles
        :param job_name: Name of the job
        :param mesh_terms: MeSH terms to be harvested
        :param terms_to_harvest: All mesh_terms previously harvested
        """
        harvester = HarvestEntrezWrapper(dataset_id, terms_to_harvest, self._temp_dir, date_from, date_to,
                                         self._mongodb_host, self._mongodb_port, self._mongodb_db_name)
        harvester.run()
        available_collections_per_source = self._get_harvested_pubmed_collections(dataset_id,
                                                                                  date_to,
                                                                                  date_from)
        harvested_pmids = self._remove_already_harvested_pubmed_articles(available_collections_per_source)
        if DEBUG:
            for source, collection in available_collections_per_source.items():
                if source == "pmc":
                    self._mongodb_manager.prune_collection(collection, 1)
                else:
                    self._mongodb_manager.prune_collection(collection, 10)
        for source, collection in available_collections_per_source.items():
            self._set_basic_medknow_settings()
            if source == "pubmed_MeSH":
                self._set_edge_specific_medknow_settings(collection, job_name, source)
            else:
                self._set_pubmed_medknow_settings(collection, dataset_id, source)

            self._run_medknow()
            if source != "pubmed_MeSH":
                self._update_pmids(source, harvested_pmids[source])

        self._update_job_metadata(job_name, mesh_terms, date_to)
