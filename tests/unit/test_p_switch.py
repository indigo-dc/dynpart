from dynpart.bin.p_switch import Switch
import os
import sys
import unittest
import commands
import tempfile
import shutil


class TestSwitch(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.conf_file = '/etc/indigo/dynpart/dynp.conf'
        self.opt = 'to_batch'
        self.listfile = os.path.join(self.test_dir, 'listfile')

        L = ["wn-206-01-01-02-b.cr.cnaf.infn.it", "blahblah"]
        lf = open(self.listfile, 'w')
        lf.write('\n'.join(L))
        lf.flush()

        self.sw = Switch(self.conf_file, self.opt, self.listfile)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_not_valid_b_host(self):
        wrong_host = "blahblah"
        cmd = """bhosts %s """ % wrong_host
        e, o = commands.getstatusoutput(cmd)
        if e:
            output = False
        output = True

        self.assertTrue(output, self.sw.check_valid_b_host(wrong_host))

    def test_valid_b_host(self):
        right_host = "wn-206-01-01-02-b.cr.cnaf.infn.it"
        cmd = """bhosts %s """ % right_host
        e, o = commands.getstatusoutput(cmd)
        if e:
            output = False
        output = True

        self.assertTrue(output, self.sw.check_valid_b_host(right_host))

    def test_valid_b_list(self):
        expected_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
        list_returned = self.sw.get_valid_b_list()
        self.assertListEqual(expected_list, self.sw.get_valid_b_list())
        self.assertIn('wn-206-01-01-02-b.cr.cnaf.infn.it', list_returned)
        self.assertNotIn('blahblah', list_returned)

    def test_valid_cn_list(self):
        expected_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
        list_returned = self.sw.get_valid_cn_list()
        self.assertListEqual(expected_list, self.sw.get_valid_cn_list())
        self.assertIn('wn-206-01-01-02-b.cr.cnaf.infn.it', list_returned)
        self.assertNotIn('blahblah', list_returned)

    def test_switch_to_cloud(self):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"],
                     "B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"],
                     "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [],
                     "C2B_TTL": {}, "B2C": []}
        self.sw.farm_json_dict = json_dict
        B_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
        C_list = ["wn-206-01-01-01-b.cr.cnaf.infn.it"]
        self.assertListEqual([], self.sw.pre_switch_action(
            'B2CR', 'C', C_list)['B2CR'])
        self.assertListEqual(B_list, self.sw.pre_switch_action(
            'B2CR', 'C', B_list)['B2CR'])

    def test_switch_to_batch(self):
        json_dict = {"C": ["wn-206-01-01-01-b.cr.cnaf.infn.it"],
                     "B": ["wn-206-01-01-02-b.cr.cnaf.infn.it"],
                     "B2CR": [], "C2BR": [], "C2B": [], "FB": [], "FC": [],
                     "C2B_TTL": {}, "B2C": []}
        self.sw.farm_json_dict = json_dict
        B_list = ["wn-206-01-01-02-b.cr.cnaf.infn.it"]
        C_list = ["wn-206-01-01-01-b.cr.cnaf.infn.it"]
        self.assertListEqual([], self.sw.pre_switch_action(
            'C2BR', 'B', B_list)['C2BR'])
        self.assertListEqual(C_list, self.sw.pre_switch_action(
            'C2BR', 'B', C_list)['C2BR'])


if __name__ == '__main__':
    unittest.main()
