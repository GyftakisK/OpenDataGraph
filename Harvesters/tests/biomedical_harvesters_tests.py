import unittest
import os
import datetime
from unittest.mock import MagicMock
from Harvesters.biomedical_harvesters import HarvestDrugBankWrapper, HarvestOBOWrapper, HarvestEntrezWrapper


class HarvestersTestSuite(unittest.TestCase):

    def test_drugbank(self):
        harvester = HarvestDrugBankWrapper("/test_path/DrugBank.xml",
                                           mongo_host="127.0.0.1",
                                           mongo_host_port=27017,
                                           mongo_dbname="test",
                                           mongo_collection="test_DrugBank")
        harvester._run_jar = MagicMock(return_value="SUCCESS")
        harvester._clean_settings_file = MagicMock()
        harvester.run()
        self.assertTrue(os.path.exists(harvester._settings_file))
        with open(harvester._settings_file, 'r') as f:
            print(f.read())
        os.remove(harvester._settings_file)

    def test_obo(self):
        harvester = HarvestOBOWrapper("/test_path/doid.obo",
                                      mongo_host="127.0.0.1",
                                      mongo_host_port=27017,
                                      mongo_dbname="test")
        harvester._run_jar = MagicMock(return_value="SUCCESS")
        harvester._clean_settings_file = MagicMock()
        harvester.run()
        self.assertTrue(os.path.exists(harvester._settings_file))
        with open(harvester._settings_file, 'r') as f:
            print(f.read())
        os.remove(harvester._settings_file)

    def test_entrez(self):
        harvester = HarvestEntrezWrapper("DMD",
                                         "Muscular Dystrophy, Duchenne",
                                         "/test_path/",
                                         datetime.date(2020, 4, 15),
                                         mongo_host="127.0.0.1",
                                         mongo_host_port=27017,
                                         mongo_dbname="test")
        harvester._run_jar = MagicMock(return_value="SUCCESS")
        harvester._clean_settings_file = MagicMock()
        harvester.run()
        print(harvester._run_jar.call_args)
        self.assertTrue(os.path.exists(harvester._settings_file))
        with open(harvester._settings_file, 'r') as f:
            print(f.read())
        os.remove(harvester._settings_file)


if __name__ == '__main__':
    unittest.main()