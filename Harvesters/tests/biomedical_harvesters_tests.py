import unittest
import os
from unittest.mock import MagicMock
from Harvesters.biomedical_harvesters import HarvestDrugBankWrapper


class HarvestersTestSuite(unittest.TestCase):

    def test_drugbank(self):
        harvester = HarvestDrugBankWrapper("/home/gyftakiskon/diploma/files/DrugBank.xml",
                                           mongo_host="127.0.0.1",
                                           mongo_host_port=27017,
                                           mongo_dbname="test",
                                           mongo_collection="test_DrugBank")
        harvester._run_jar = MagicMock(return_value="SUCCESS")
        harvester.run()
        self.assertFalse(os.path.exists(harvester._settings_file))


if __name__ == '__main__':
    unittest.main()