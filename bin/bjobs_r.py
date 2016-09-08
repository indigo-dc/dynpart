#!/usr/bin/env python

import commands
import sys

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

e,o = commands.getstatusoutput('bjobs -noheader -u all -w -r')
if e or o.endswith('No running job found'):
    sys.exit(1)

RJ = [[x[0], x[1], x[5]] for x in [l.split() for l in o.split('\n')]]

print '\n'.join([repr(t) for t in RJ])
