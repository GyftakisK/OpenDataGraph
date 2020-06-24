import yaml
import os
from utilities import run_jar, get_filename_from_file_path


class HarvesterWrapper:
    def __init__(self, harvester_jar_name, mongo_host, mongo_host_port, mongo_dbname):
        self._harvester_jar = os.path.join(os.path.dirname(os.path.realpath(__file__)), harvester_jar_name)
        self._mongo_config = {"host": mongo_host,
                              "port": mongo_host_port,
                              "dbname": mongo_dbname}
        self._settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.yaml")

    def run(self):
        self._create_settings_file()
        args = self._get_jar_arguments()
        output = self._run_jar(args)
        self._check_output(output)
        self._clean_settings_file()

    def _create_settings_file(self):
        settings = self._get_settings()
        with open(self._settings_file, 'w') as settings_file:
            yaml.dump(settings, settings_file)

    def _run_jar(self, args):
        return run_jar(self._harvester_jar, args)

    def _clean_settings_file(self):
        os.remove(self._settings_file)

    def _get_jar_arguments(self):
        raise NotImplemented

    def _get_settings(self):
        raise NotImplemented

    def _check_output(self, output):
        pass


class HarvestDrugBankWrapper(HarvesterWrapper):
    def __init__(self, file_path, mongo_host, mongo_host_port, mongo_dbname, mongo_collection):
        super().__init__("HarvestDrugBank.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._mongo_config["collection"] = mongo_collection
        self._file_path = file_path

    def _get_settings(self):
        return {"inputFilePath": self._file_path, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return [self._settings_file]


class HarvestOBOWrapper(HarvesterWrapper):
    def __init__(self, file_path, mongo_host, mongo_host_port, mongo_dbname):
        super().__init__("HarvestOBO.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._base_folder = os.path.dirname(os.path.realpath(file_path))
        filename = get_filename_from_file_path(file_path)
        self._input_obo_name = filename.replace(".obo", "") if ".obo" in filename else filename

    @property
    def input_obo_name(self):
        return self._input_obo_name

    def _get_settings(self):
        return {"baseFolder": self._base_folder, "inputOBOName": self._input_obo_name, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return [self._settings_file]


class HarvestEntrezWrapper(HarvesterWrapper):
    def __init__(self, dataset_id, mesh_terms, base_dir, date_from, date_to,  mongo_host, mongo_host_port, mongo_dbname):
        super().__init__("HarvestEntrez.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._base_folder = base_dir
        self._dates = {"from": date_from.strftime("%Y/%m/%d"), "to": date_to.strftime("%Y/%m/%d")}
        self._dataset_id = dataset_id
        self._mesh_terms = mesh_terms if type(mesh_terms) == list else [mesh_terms]

    def _get_settings(self):
        return {"baseFolder": self._base_folder, "date": self._dates, "meshTerms": self._mesh_terms,
                "datasetId": self._dataset_id, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return [self._settings_file]
