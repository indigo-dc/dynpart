#!/usr/bin/env python
import os
import sys
import commands
import re
from dynp_common import mlog, get_jsondict, put_jsondict, get_value

"""Copyright (c) 2015 INFN - INDIGO-DataCloud
All Rights Reserved
Licensed under the Apache License, Version 2.0;
you may not use this file except in compliance with the
License. You may obtain a copy of the License at:
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
See the License for the specific language governing
permissions and limitations under the License."""


def help():
    print """"usage: adjust_lsf_shares.py 'u_cms' 100\n
    Makes the relative adjustments of lsf shares wrt slot
    reductions for a particular user group while keeping
    the shares of others unaffected
"""


class Fairshare(object):

    def __init__(self, conf_file, user_group, slot_reduction):
        self.conf_file = conf_file
        self.user_group = user_group
        self.slot_reduction = slot_reduction
        self.jc = get_jsondict(self.conf_file)
        lgdict = get_value(self.jc, 'logging')

        log_dir = get_value(lgdict, 'log_dir')
        if not os.path.isdir(log_dir):
            print "Please check the %s directory" % log_dir
            sys.exit(1)
        log_filename = get_value(lgdict, 'log_file')
        self.log_file = os.path.join(log_dir, log_filename)
        self.logf = open(self.log_file, 'a')
        fsdict = get_value(self.jc, 'fairshare')
        self.part_name = get_value(fsdict, 'partition_name')
        self.p1 = get_value(fsdict, 'pattern1')
        self.p2 = get_value(fsdict, 'pattern2')
        self.lsb_file = get_value(fsdict, 'lsb_file')
        self.temp_lsb_file = get_value(fsdict, 'temp_lsb_file')
        self.blacklist = get_value(fsdict, 'blacklist')
        self.shareDict = {}

    def calculate_total_slots(self):
        cmd = """bhosts -w -R "select [dynp==1]" %s |
        awk '{s+=$4}END{print s}'""" % (self.part_name)
        e, o = commands.getstatusoutput(cmd)
        if e:
            mlog(self.logf, "./bhost Failed!")
        total_slots = int(o)
        return total_slots

    def read_file(self):
        shareList = []
        temp_d = {}
        with open(self.lsb_file) as infile:
            flag = False
            for line in infile:
                sec = line.split('=')
                if (sec[0].strip() == self.p1) and (sec[1].strip() ==
                                                    self.part_name):
                    flag = False
                elif (sec[0].strip() == self.p2) and (sec[1].strip() == "(\\"):
                    flag = True
                elif line.strip() == ")":
                    flag = False
                elif line.strip() == "End HostPartition":
                    break
                elif flag:
                    splitline = line.strip().split()
                    shareList = shareList + \
                        [(splitline[0].strip('[').strip(','), int(
                            splitline[1].strip('\\').strip(']')))]
        temp_d = dict(shareList)
        for k in self.blacklist:
            temp_d.pop(k)
        self.shareList = temp_d.items()
        self.sumShare = sum(v for k, v in self.shareList)
        return self.shareList

    def make_initial_dict(self, total_slots):
        for key, value in self.shareList:
            self.shareDict[key] = {}
            sharePercent = round(value * 100.00 / self.sumShare, 5)
            numSlots = int(round(value * total_slots * 1.00 / self.sumShare))
            self.shareDict[key]["share"] = value
            self.shareDict[key]["sharePercent"] = sharePercent
            self.shareDict[key]["numSlots"] = numSlots
        return self.shareDict

    def update_dict(self, total_slots):
        if self.user_group not in self.shareDict:
            print 'user_group  %s is not defined' % self.user_group
            sys.exit(1)
        if 'numSlots' not in self.shareDict[self.user_group]:
            print 'numSlots is not defined for ug % s' % self.user_group
            sys.exit(1)

        delta = total_slots * 1.0 / self.sumShare
        new_numSlots = int(self.shareDict[self.user_group][
                           'numSlots'] - self.slot_reduction)
        new_share = int(round(new_numSlots / delta, 0))
        self.shareDict[self.user_group]['numSlots'] = new_numSlots
        self.shareDict[self.user_group]['share'] = new_share

        for key, value in enumerate(self.shareList):
            if value[0] == self.user_group:
                temp = list(self.shareList[key])
                temp[1] = self.shareDict[self.user_group]['share']
                self.shareList[key] = tuple(temp)
        self.revised_sumShare = sum(v for k, v in self.shareList)

        for key, value in self.shareList:
            new_sharePercent = round(value * 100.00 / self.revised_sumShare, 5)
            self.shareDict[key]["sharePercent"] = new_sharePercent
        print "------------------After share update---------------------------"
        new_shareDict_sorted_by_share = sorted(
            self.shareDict.items(), key=lambda x: x[1]['share'], reverse=True)
        for element in new_shareDict_sorted_by_share:
            print element
        return self.shareDict

    def write_back_to_file(self, updated_shareDict):
        infile = open(self.lsb_file)
        while True:
            pos = infile.tell()
            line = infile.readline()
            sec = line.split('=')
            found = False
            if (sec[0].strip() == self.p1) and (sec[1].strip() ==
                                                self.part_name):
                pos_0 = pos
            elif (sec[0].strip() == self.p2) and (sec[1].strip() == "(\\"):
                pos_start = pos
            elif (line.strip() == "End HostPartition"):
                pos_end = pos
                break
            elif line == '':
                break

        outfile = open(self.temp_lsb_file, 'w')
        shL = updated_shareDict.items()
        shL.sort()
        replaced_str = "USER_SHARES = (\\\n" + ''.join("\t\t[% s, % d]\\\n" % (k, 9631) for k in self.blacklist) + ''.join(
            "\t\t[ % s, % d]\\\n" % (k, v['share']) for (k, v) in shL) + "\t\t)\n\n"
        infile.seek(0)
        outfile.write(infile.read(pos_start))
        outfile.write(replaced_str)
        infile.seek(pos_end)
        outfile.write(infile.read())
        outfile.close()
        infile.close()
        print "***New content is written into file % s***" % self.temp_lsb_file


def main():
    if len(sys.argv) <= 2:
        help()
        sys.exit(0)

    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    user_group = sys.argv[1]
    slot_reduction = int(sys.argv[2])

    fs = Fairshare(conf_file, user_group, slot_reduction)
#    total_slots = fs.calculate_total_slots()
    total_slots = 24567
    shareList = fs.read_file()
    shareDict = fs.make_initial_dict(total_slots)
    shareDict_sorted_by_share = sorted(fs.shareDict.items(), key=lambda x: x[
                                       1]['share'], reverse=True)
    print "--------------------Before share update----------------------------"
    for element in shareDict_sorted_by_share:
        print element
    updated_shareDict = fs.update_dict(total_slots)
    fs.write_back_to_file(updated_shareDict)

if __name__ == "__main__":
    main()
