#!/usr/bin/env python

# @@@ START COPYRIGHT @@@
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# @@@ END COPYRIGHT @@@

### this script should be run on all nodes with sudo user ###

import re
import json
import sys
import os
import platform
from common import run_cmd, cmd_output, err, Version

class Check(object):
    """ check system envs """

    def __init__(self, dbcfgs_json):
        self.dbcfgs = json.loads(dbcfgs_json)
        self.version = Version()

    def check_linux(self):
        """ check Linux version """
        os_dist, os_ver = platform.dist()[:2]

        if os_dist not in self.version.get_version('linux'):
            err('Linux distribution %s doesn\'t support' % os_dist)
        else:
            if not os_ver.split('.')[0] in self.version.get_version(os_dist):
                err('%s version %s doesn\'t support' % (os_dist, os_ver))

    def check_sudo(self):
        """ check sudo access """
        run_cmd('sudo -n echo -n "check sudo access" > /dev/null 2>&1')

    def check_hbase_xml(self):
        """ check if hbase-site.xml file exists """
        hbase_xml_file = self.dbcfgs['hbase_xml_file']
        if not os.path.exists(hbase_xml_file):
            err('HBase xml file is not found')

    def check_java(self):
        """ check JDK version """
        jdk_ver = cmd_output('javac -version')
        try:
            jdk_ver = re.search('(\d\.\d)', jdk_ver).groups()[0]
        except AttributeError:
            err('No JDK found')

        if self.dbcfgs['req_java8'] == 'Y': # only allow JDK1.8
            support_java = ['1.8']
        else:
            support_java = self.version.get_version('java')

        if jdk_ver not in support_java:
            err('Unsupported JDK version %s' % jdk_ver)


    def check_traf_proc(self):
        """ check if previous installed trafodion processes exist """
        mon_process = cmd_output('ps -ef|grep -c "monitor COLD"')
        if int(mon_process) > 1:
            err('Trafodion process is found, please stop it first')

    def check_hbase_ver(self):
        """ check Apache HBase version if Apache Hadoop """
        pass


def run():
    PREFIX = 'check_'
    check = Check(dbcfgs_json)

    # call method
    [getattr(check, m)() for m in dir(check) if m.startswith(PREFIX)]

# main
try:
    dbcfgs_json = sys.argv[1]
except IndexError:
    err('No db config found')
run()
