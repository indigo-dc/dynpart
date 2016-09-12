from p_driver_cls import Driver
import os
import sys
import unittest
import tempfile
import shutil


class TestSwitch(unittest.TestCase):

    def setUp(self):
        self.conf_file = '/etc/indigo/dynpart/dynp.conf'
        self.json_dict = {"C": [], "B": ["wn-206-01-01-01-b.cr.cnaf.infn.it"],
                          "B2CR": [], "C2BR": [], "C2B": [], "FB": [],
                          "FC": [], "C2B_TTL": {},
                          "B2C": ["wn-206-01-01-02-b.cr.cnaf.infn.it"]}

        self.d = Driver(self.conf_file)

    def test_make_switch_b2c(self):
        self.d.farm_json_dict = self.json_dict
        self.assertFalse(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['C'])
        self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'C', 'B2C')
        print self.d.farm_json_dict
        self.assertTrue(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['C'])
        self.assertTrue(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" not in
            self.d.farm_json_dict['B2C'])

    def test_make_switch_c2b(self):
        self.d.farm_json_dict = self.json_dict
        self.assertFalse(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['B'])
        self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'B', 'C2B')
        print self.d.farm_json_dict
        self.assertTrue(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['B'])
        self.assertTrue(
            "wn-206-01-01-02-b.cr.cnaf.infn.it" not in
            self.d.farm_json_dict['C2B'])

    def test_enable_nova(self):
        hostN = "wn-206-01-01-02-b.cr.cnaf.infn.it"
        self.d.enable_nova(hostN)
        dis_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list(
        ) if x.status == "disabled"]
        ena_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list()
                 if x.status == "enabled"]
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in ena_L)
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in dis_L)
        self.d.disable_nova(hostN)

    def test_disable_nova(self):
        hostN = "wn-206-01-01-02-b.cr.cnaf.infn.it"
        self.d.disable_nova(hostN)
        dis_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list(
        ) if x.status == "disabled"]
        ena_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list()
                 if x.status == "enabled"]
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in dis_L)
        self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in ena_L)
        self.d.enable_nova(hostN)

    def test_count_n_vm(self):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        expected_count = [x.running_vms for x in self.d.nova.hypervisors.list(
        ) if x.hypervisor_hostname == hostN][0]
        self.assertEqual(expected_count, self.d.count_N_vm(hostN))

    def test_stop_running_vm(self):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        self.d.stop_running_vm(hostN)
        time.sleep(10)
        self.assertEqual(0, self.d.count_N_vm(hostN))

if __name__ == '__main__':
    unittest.main()
