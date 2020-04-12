import yaml
import os
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
        args = self._get_arguments()
        output = self._run_jar(args)
        print(output)
        self._clean_settings_file()

    def _create_settings_file(self):
        raise NotImplemented

    def _get_arguments(self):
        raise NotImplemented

    def _run_jar(self, args):
        return run_jar(self._harvester_jar_name, args)

    def _clean_settings_file(self):
        raise NotImplemented


class HarvestDrugBankWrapper(HarvesterWrapper):
    def __init__(self, file_path, mongo_host, mongo_host_port, mongo_dbname, mongo_collection):
        super().__init__("HarvestDrugBank.jar", mongo_host, mongo_host_port, mongo_dbname)
        self._mongo_config["collection"] = mongo_collection
        self._file_path = file_path

    def _create_settings_file(self):
        settings = {"inputFilePath": self._file_path, "mongodb": self._mongo_config}
        with open(self._settings_file, 'w') as settings_file:
            yaml.dump(settings, settings_file)

    def _get_arguments(self):
        return self._settings_file

    def _clean_settings_file(self):
        os.remove(self._settings_file)
