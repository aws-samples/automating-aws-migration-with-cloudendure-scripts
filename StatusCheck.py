# Copyright 2008-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import sys
import requests
import json
import yaml
import os


def check(launchtype, cloud_endure, projectname, configfile):
    project_id = cloud_endure.get_project_id(projectname)
    with open(configfile, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    machines_info = cloud_endure.get_machine_list(project_id)
    env = 'TEST' if launchtype == 'test' else 'PROD'
    launch_datetime = 'lastTestLaunchDateTime' if launchtype == 'test' else 'lastCutoverDateTime'
    machines_count = 0

    for i in range(1, config["project"]["machinecount"] + 1):
        index = "machine" + str(i)
        name = config[index]["machineName"]
        if name in machines_info.keys():
            if 'lastConsistencyDateTime' not in machines_info[name]['replicationInfo'].keys():
                print("Machine: " + name + " replication in progress, please wait for a few minutes....")
            else:
                migrated = " has NOT been "
                if launch_datetime in machines_info[name]["lifeCycle"].keys():
                    migrated = " has been "
                    machines_count += 1
                print("Machine: " + machines_info[name]['sourceProperties']['name'] +
                      migrated + "migrated to the " + env + " environment....")
        else:
            print("ERROR: Machine: " + name + " does not exist....")

    if machines_count == config["project"]["machinecount"]:
        print("All Machines in the config file have been migrated to the " + env + " environment....")
    else:
        print("*WARNING*: Some machines in the config file have NOT been migrated to the " + env + " environment....")
