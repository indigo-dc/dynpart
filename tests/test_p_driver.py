from p_driver_cls import Driver
import os
import sys
import unittest
import tempfile
import shutil

class TestSwitch(unittest.TestCase):
    def setUp(self):
        self.conf_file = '/etc/indigo/dynpart/dynp.conf'
        self.d = Driver(self.conf_file)

#    def tearDown(self):
#        shutil.rmtree(self.test_dir)

    # def test_make_switch_b2c(self):
    #     json_dict = {"C": [], "B": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [], "C2B_TTL": {}, "B2C": ["wn-206-01-01-02-b.cr.cnaf.infn.it"]}
    #     self.d.farm_json_dict = json_dict
    #     self.assertFalse("wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['C'])
    #     self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'C', 'B2C')
    #     print self.d.farm_json_dict
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['C'])
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in self.d.farm_json_dict['B2C'])

    # def test_make_switch_c2b(self):
    #     json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"], "B": [], "B2CR": [], "C2BR": [], "C2B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"], "FB": [], "FC": [], "C2B_TTL": {"wn-206-01-01-02-b.cr.cnaf.infn.it" : 1473678420}, "B2C": []}
    #     self.d.farm_json_dict = json_dict
    #     self.assertFalse("wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['B'])
    #     self.d.make_switch("wn-206-01-01-02-b.cr.cnaf.infn.it", 'B', 'C2B')
    #     print self.d.farm_json_dict        
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in self.d.farm_json_dict['B'])
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in self.d.farm_json_dict['C2B'])

    # def test_enable_nova(self):
    #     hostN = "wn-206-01-01-02-b.cr.cnaf.infn.it"
    #     self.d.enable_nova(hostN)
    #     dis_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list() if x.status == "disabled"]
    #     ena_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list() if x.status == "enabled"]
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in ena_L)
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in dis_L)
    #     self.d.disable_nova(hostN)

    # def test_disable_nova(self):
    #     hostN = "wn-206-01-01-02-b.cr.cnaf.infn.it"
    #     self.d.disable_nova(hostN)
    #     dis_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list() if x.status == "disabled"]
    #     ena_L = [x.hypervisor_hostname for x in self.d.nova.hypervisors.list() if x.status == "enabled"]
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" in dis_L)
    #     self.assertTrue("wn-206-01-01-02-b.cr.cnaf.infn.it" not in ena_L)
    #     self.d.enable_nova(hostN)

    def test_count_n_vm(self):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        expected_count = [x.running_vms for x in self.d.nova.hypervisors.list() if x.hypervisor_hostname == hostN][0]
        self.assertEqual(expected_count, self.d.count_N_vm(hostN))

    def test_stop_running_vm(self):
        hostN = "wn-206-01-01-01-b.cr.cnaf.infn.it"
        self.d.stop_running_vm(hostN)
        time.sleep(10)
        self.assertEqual(0, self.d.count_N_vm(hostN))

#        print self.d.count_N_vm(hostN)



    # def test_valid_b_host(self):
    #     right_host = "wn-206-01-01-02-b.cr.cnaf.infn.it"
    #     cmd = """bhosts %s """ % right_host
    #     e, o = commands.getstatusoutput(cmd)
    #     if e:
    #         output = False
    #     output = True

    #     self.assertTrue(output, self.sw.check_valid_b_host(right_host))
        
    # def test_valid_b_list(self):
    #     expected_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
    #     list_returned = self.sw.get_valid_b_list()
    #     self.assertListEqual(expected_list, self.sw.get_valid_b_list())
    #     self.assertIn('wn-206-01-01-02-b.cr.cnaf.infn.it', list_returned)
    #     self.assertNotIn('blahblah', list_returned)

    # def test_valid_cn_list(self):
    #     expected_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
    #     list_returned = self.sw.get_valid_cn_list()
    #     self.assertListEqual(expected_list, self.sw.get_valid_cn_list())
    #     self.assertIn('wn-206-01-01-02-b.cr.cnaf.infn.it', list_returned)
    #     self.assertNotIn('blahblah', list_returned)


    # def test_switch_to_cloud(self):
    #     B_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
    #     C_list = ["wn-206-01-01-01-b.cr.cnaf.infn.it"]
    #     self.assertListEqual([], self.sw.pre_switch_action('B2CR', 'C', C_list)['B2CR'])
    #     self.assertListEqual(B_list, self.sw.pre_switch_action('B2CR', 'C', B_list)['B2CR'])

    # def test_switch_to_batch(self):
    #     B_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
    #     C_list = ["wn-206-01-01-01-b.cr.cnaf.infn.it"]
    #     self.assertListEqual([], self.sw.pre_switch_action('C2BR', 'B', B_list)['C2BR'])
    #     self.assertListEqual(C_list, self.sw.pre_switch_action('C2BR', 'B', C_list)['C2BR'])


if __name__ == '__main__':
    unittest.main()
