from dynpart.bin.dynp_common import *
import time
import os
import sys
import json
import unittest
import shutil
import tempfile


class TestDynpCommon(unittest.TestCase):

    def setUp(self):
        self.t = time.time()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_now(self):
        self.assertEqual(now(),
                         time.asctime(time.localtime(self.t)))
        self.assertEqual(int(time.mktime(time.localtime(self.t))),
                         int(self.t))

    def test_mlog(self):
        script_name = os.path.basename(sys.argv[0])
        f = open(os.path.join(self.test_dir, 'test.txt'), 'a')
        mlog(f, "Please check the path of the file")
        f = open(os.path.join(self.test_dir, 'test.txt'))
        self.assertEqual(f.read(), "%s %s:" % (
            now(), script_name) + 'Please check the path of the file' + '\n')

    def test_get_jsondict(self):
        json_file = os.path.join(self.test_dir, 'test.txt')
        resulting_dict = {"Alpha": ["A", "B"], "Numbers": [1, 2]}
        with open(json_file, 'w') as f:
            json.dump(resulting_dict, f)
        expected_dict = get_jsondict(json_file)
        self.assertDictEqual(resulting_dict, expected_dict)

    def test_put_jsondict(self):
        json_file = os.path.join(self.test_dir, 'test.txt')
        mydict = {"Alpha": ["A", "B"], "Numbers": [1, 2]}
        put_jsondict(json_file, mydict)
        mydict_2 = json.load(open(json_file, 'r'))
        self.assertDictEqual(mydict_2, mydict)
        self.assertEqual(mydict_2['Numbers'], mydict['Numbers'])
        self.assertIn('Numbers', mydict_2)
        self.assertNotIn('Romans', mydict_2)
        self.assertEqual(len(mydict_2), 2)
        self.assertTrue("Alpha" in mydict_2)
        self.assertFalse("blah" in mydict_2)

    def test_get_value(self):
        mydict = {"Alpha": "Z", "Numbers": 42}
        self.assertEqual(mydict["Numbers"], get_value(mydict, 'Numbers'))
        self.assertTrue(get_value(mydict, 'Numbers'))

if __name__ == '__main__':
    unittest.main()
