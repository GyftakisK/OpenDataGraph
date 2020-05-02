import unittest
import os
import datetime
from unittest.mock import MagicMock
from harvesters.biomedical_harvesters import HarvestDrugBankWrapper, HarvestOBOWrapper, HarvestEntrezWrapper


class HarvestersTestSuite(unittest.TestCase):
    def assert_harvester_settings(self, harvester, expected_settings):
        harvester._run_jar = MagicMock(return_value="SUCCESS")
        harvester._clean_settings_file = MagicMock()
        harvester.run()
        self.assertTrue(os.path.exists(harvester._settings_file))
        with open(harvester._settings_file, 'r') as f:
            output = f.read()
        for setting in expected_settings:
            self.assertIn(setting, output)
        os.remove(harvester._settings_file)

    def test_drugbank(self):
        harvester = HarvestDrugBankWrapper("/test_path/DrugBank.xml",
                                           mongo_host="127.0.0.1",
                                           mongo_host_port=27017,
                                           mongo_dbname="test",
                                           mongo_collection="test_DrugBank")
        expected_settings = [
            "inputFilePath: /test_path/DrugBank.xml",
            "mongodb: {collection: test_DrugBank, dbname: test, host: 127.0.0.1, port: 27017}"
        ]
        self.assert_harvester_settings(harvester, expected_settings)

    def test_obo(self):
        harvester = HarvestOBOWrapper("/test_path/doid.obo",
                                      mongo_host="127.0.0.1",
                                      mongo_host_port=27017,
                                      mongo_dbname="test")
        expected_settings = [
            "baseFolder: /test_path",
            "inputOBOName: doid",
            "mongodb: {dbname: test, host: 127.0.0.1, port: 27017}"
        ]
        self.assert_harvester_settings(harvester, expected_settings)

    def test_entrez_1(self):
        harvester = HarvestEntrezWrapper("DMD",
                                         "Muscular Dystrophy, Duchenne",
                                         "/test_path/",
                                         datetime.date(2020, 4, 15),
                                         datetime.date(2020, 5, 15),
                                         mongo_host="127.0.0.1",
                                         mongo_host_port=27017,
                                         mongo_dbname="test")
        expected_settings = [
            "baseFolder: /test_path/",
            "date: {from: 2020/04/15, to: 2020/05/15}",
            "datasetId: DMD",
            "meshTerms: ['Muscular Dystrophy, Duchenne']",
            "mongodb: {dbname: test, host: 127.0.0.1, port: 27017}"
        ]
        self.assert_harvester_settings(harvester, expected_settings)

    def test_entrez_2(self):
        harvester = HarvestEntrezWrapper("UPDATE",
                                         ["Muscular Dystrophy, Duchenne", "Lung Cancer"],
                                         "/test_path/",
                                         datetime.date(2020, 4, 15),
                                         datetime.date(2020, 5, 15),
                                         mongo_host="127.0.0.1",
                                         mongo_host_port=27017,
                                         mongo_dbname="test")
        expected_settings = [
            "baseFolder: /test_path/",
            "date: {from: 2020/04/15, to: 2020/05/15}",
            "datasetId: UPDATE",
            "meshTerms: ['Muscular Dystrophy, Duchenne', Lung Cancer]",
            "mongodb: {dbname: test, host: 127.0.0.1, port: 27017}"
        ]
        self.assert_harvester_settings(harvester, expected_settings)


if __name__ == '__main__':
    unittest.main()