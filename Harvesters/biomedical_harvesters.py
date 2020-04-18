import yaml
import os
import ntpath
import datetime
from utilities import run_jar


class HarvesterWrapper:
    def __init__(self, harvester_jar_name, mongo_host, mongo_host_port, mongo_dbname):
        self._harvester_jar_name = harvester_jar_name
        self._mongo_config = {"host": mongo_host,
                              "port": mongo_host_port,
                              "dbname": mongo_dbname}
        self._settings_file = "settings.yaml"

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
        return run_jar(self._harvester_jar_name, args)

    def _clean_settings_file(self):
        os.remove(self._settings_file)

    def _get_jar_arguments(self):
        raise NotImplemented

    def _get_settings(self):
        raise NotImplemented

    def _check_output(self, output):
        pass


class HarvestDrugBankWrapper(HarvesterWrapper):
    def __init__(self, file_path, mongo_host, mongo_host_port, mongo_dbname, mongo_collection="DrugBank"):
        super().__init__("HarvestDrugBank.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._mongo_config["collection"] = mongo_collection
        self._file_path = file_path

    def _get_settings(self):
        return {"inputFilePath": self._file_path, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return self._settings_file


class HarvestOBOWrapper(HarvesterWrapper):
    def __init__(self, file_path, mongo_host, mongo_host_port, mongo_dbname):
        super().__init__("HarvestOBO.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._base_folder = os.path.abspath(file_path)
        self._input_obo_name = ntpath.basename(file_path).strip(".obo")

    def _get_settings(self):
        return {"baseFolder": self._base_folder, "inputOBOName": self._input_obo_name, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return self._settings_file


class HarvestEntrezWrapper(HarvesterWrapper):
    def __init__(self, dataset_id, mesh_term, base_dir, last_update,  mongo_host, mongo_host_port, mongo_dbname):
        super().__init__("HarvestOBO.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._base_folder = base_dir
        self._last_update = last_update.strftime("%Y/%m/%d")
        self._dataset_id = dataset_id
        self._mesh_term = mesh_term

    def _get_settings(self):
        return {"baseFolder": self._base_folder, "lastUpdate": self._last_update, "mongodb": self._mongo_config}

    def _get_jar_arguments(self):
        return self._dataset_id, self._mesh_term, datetime.datetime.now().strftime("%Y/%m/%d")
