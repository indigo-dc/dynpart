from dynpart.bin.p_driver import Driver
import os
import sys
import unittest
import tempfile
import shutil
import commands
import mock
from mock import patch


class TestDriver(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
#        self.conf_file = '/etc/indigo/dynpart/dynp.conf'
        self.conf_file = '/home/CMS/sonia.taneja/mygit/dynpart/dynpart/etc/dynp.conf'
        self.d = Driver(self.conf_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_isError_true(self):
        self.d.rj_file = os.path.join(self.test_dir, 'bjobs_r.out')
        with open(self.d.rj_file, 'w') as outfile:
            outfile.write("Error running bjobs")
        result = self.d.isError()
        self.assertTrue(result)

    def test_isError_False(self):
        self.d.rj_file = os.path.join(self.test_dir, 'bjobs_r.out')
        with open(self.d.rj_file, 'w') as outfile:
            outfile.write("[150959360, alicesgm042, wn-205-03-23-01-b]")
        result = self.d.isError()
        self.assertFalse(result)

    @patch('dynpart.bin.p_driver.Driver.count_N_jobs')
    def test_count_N_jobs(self, count_jobs_mock):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        count_jobs_mock.return_value = 10
        expected_count = 10
        self.assertEqual(expected_count, self.d.count_N_jobs(hostN))

    def test_make_switch_b2c(self):
        json_dict = {"C": [], "B": ["wn-206-01-01-01-b.cr.cnaf.infn.it"],
                     "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [],
                     "C2B_TTL": {},
                     "B2C": ["wn-206-01-01-02-b.cr.cnaf.infn.it"]}
        self.d.farm_json_dict = json_dict
        self.assertFalse(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['C'])
        self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'C', 'B2C')
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it"
                        in self.d.farm_json_dict['C'])
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it"
                        not in self.d.farm_json_dict['B2C'])

    def test_make_switch_c2b(self):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "FB": [], "FC": [], "B2C": [],
                     "C2B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"], "C2B_TTL":
                     {"wn-206-01-01-02-b.cr.cnaf.infn.it": 1473678420}}
        self.d.farm_json_dict = json_dict
        self.assertFalse("wn-206-01-01-02-b.cr.cnaf.infn.it"
                         in self.d.farm_json_dict['B'])
        self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'B', 'C2B')
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it"
                        in self.d.farm_json_dict['B'])
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it"
                        not in self.d.farm_json_dict['C2B'])

    @patch('dynpart.bin.p_driver.Driver.enable_nova')
    def test_enable_nova_compute(self, enable_nova_mock):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        enable_nova_mock.return_value = True
        result = self.d.enable_nova(hostN)
        self.assertTrue(result)

    @patch('dynpart.bin.p_driver.Driver.count_N_vm')
    def test_count_N_vm(self, count_vm_mock):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        count_vm_mock.return_value = 10
        expected_count = 10
        self.assertEqual(expected_count, self.d.count_N_vm(hostN))

    @patch('dynpart.bin.p_driver.Driver.stop_running_vm')
    def test_stop_running_vm(self, stop_running_vm_mock):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        stop_running_vm_mock.return_value = True
        result = self.d.stop_running_vm(hostN)
        self.assertTrue(result)

    @patch('dynpart.bin.p_driver.Driver.stop_running_vm')
    def test_check_c2b_ttl_expired(self, stop_running_vm_mock):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "FB": [], "FC": [], "B2C": [],
                     "C2B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"], "C2B_TTL":
                     {"wn-206-01-01-02-b.cr.cnaf.infn.it": 1473678420}}
        self.d.farm_json_dict = json_dict
        self.d.mjf_dir = self.test_dir
        mjf_file = "wn-206-01-01-02-b-cr-cnaf-infn-it_ttl"
        jff = os.path.join(self.d.mjf_dir, mjf_file)
        jf = open(jff, 'w')
        jf.flush()
        stop_running_vm_mock.return_value = True
        expected_dict = {'C2B': [], 'C': ['wn-206-01-01-01-b.cr.cnaf.infn.it'],
                         'B': ['wn-206-01-01-02-b.cr.cnaf.infn.it'], 'FC': [],
                         'C2B_TTL': {}, 'B2CR': [], 'B2C': [], 'FB': [],
                         'C2BR': []}
        result = self.d.check_c2b()
        self.assertEqual(expected_dict, result)

    @patch('dynpart.bin.p_driver.Driver.count_N_vm')
    def test_check_c2b_ttl_not_expired_count_vm_not_zero(self, count_vm_mock):
        ttl = self.d.exe_time + 600
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "FB": [], "FC": [], "B2C": [],
                     "C2B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"],
                     "C2B_TTL": {"wn-206-01-01-02-b.cr.cnaf.infn.it": ttl}}
        self.d.farm_json_dict = json_dict
        count_vm_mock.return_value = 10
        result = self.d.check_c2b()
        self.assertEqual(json_dict, result)

    @patch('dynpart.bin.p_driver.Driver.count_N_vm')
    def test_check_c2b_ttl_not_expired_count_vm_is_zero(self, count_vm_mock):
        ttl = self.d.exe_time + 600
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "FB": [], "FC": [], "B2C": [],
                     "C2B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"],
                     "C2B_TTL": {"wn-206-01-01-02-b.cr.cnaf.infn.it": ttl}}
        self.d.farm_json_dict = json_dict
        self.d.mjf_dir = self.test_dir
        mjf_file = "wn-206-01-01-02-b-cr-cnaf-infn-it_ttl"
        jff = os.path.join(self.d.mjf_dir, mjf_file)
        jf = open(jff, 'w')
        jf.flush()
        count_vm_mock.return_value = 0
        expected_dict = {'C2B': [], 'C': ['wn-206-01-01-01-b.cr.cnaf.infn.it'],
                         'B': ['wn-206-01-01-02-b.cr.cnaf.infn.it'], 'FC': [],
                         'C2B_TTL': {}, 'B2CR': [], 'B2C': [], 'FB': [],
                         'C2BR': []}
        result = self.d.check_c2b()
        self.assertEqual(expected_dict, result)

    @patch('dynpart.bin.p_driver.Driver.count_N_jobs')
    def test_check_b2c_count_jobs_not_zero(self, count_jobs_mock):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [],
                     "C2B_TTL": {},
                     "B2C": ["wn-206-01-01-02-b.cr.cnaf.infn.it"]}
        self.d.farm_json_dict = json_dict
        count_jobs_mock.return_value = 10
        result = self.d.check_b2c()
        self.assertEqual(json_dict, result)

    @patch('dynpart.bin.p_driver.Driver.enable_nova')
    @patch('dynpart.bin.p_driver.Driver.count_N_jobs')
    def test_check_b2c_count_jobs_is_zero(self,
                                          count_jobs_mock, enable_nova_mock):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [],
                     "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [],
                     "C2B_TTL": {},
                     "B2C": ["wn-206-01-01-02-b.cr.cnaf.infn.it"]}
        self.d.farm_json_dict = json_dict
        count_jobs_mock.return_value = 0
        enable_nova_mock.return_value = True
        result = self.d.check_b2c()
        expected_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it",
                               "wn-206-01-01-02-b.cr.cnaf.infn.it"],
                         "B": [], "B2CR": [], "C2BR": [], "C2B": [],
                         "FB": [], "FC": [], "C2B_TTL": {},
                         "B2C": []}
        self.assertEqual(expected_dict, result)

    @patch('dynpart.bin.p_driver.Driver.disable_nova')
    def test_disable_nova_compute(self, disable_nova_mock):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        disable_nova_mock.return_value = True
        result = self.d.disable_nova(hostN)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
