#Copyright 2008-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

#Permission is hereby granted, free of charge, to any person obtaining a copy of this
#software and associated documentation files (the "Software"), to deal in the Software
#without restriction, including without limitation the rights to use, copy, modify,
#merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import sys
import requests
import json
import yaml
import os
import datetime

def status(session, headers, endpoint, HOST, project_id, configfile, launchtype, dryrun):
    if launchtype == "test" or launchtype == "cutover":
       with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
            config = yaml.safe_load(ymlfile)
    machine_status = 0
    m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
    for i in range(1, config["project"]["machinecount"]+1):
        index = "machine" + str(i)
        machine_exist = False
        for machine in json.loads(m.text)["items"]:
           if config[index]["machineName"] == machine['sourceProperties']['name']:
              machine_exist = True
              # Check if replication is done
              if 'lastConsistencyDateTime' not in machine['replicationInfo']:
                  print("ERROR: Machine: " + machine['sourceProperties']['name'] + " replication in progress, please wait for a few minutes....")
                  sys.exit(1)
              else:
                  # check replication lag
                  a = int(machine['replicationInfo']['lastConsistencyDateTime'][11:13])
                  b = int(machine['replicationInfo']['lastConsistencyDateTime'][14:16])
                  x = int(datetime.datetime.utcnow().isoformat()[11:13])
                  y = int(datetime.datetime.utcnow().isoformat()[14:16])
                  result = (x - a) * 60 + (y - b)
                  if result > 180:
                      print("ERROR: Machine: " + machine['sourceProperties']['name'] + " replication lag is more than 180 minutes....")
                      print("- Current Replication lag for " + machine['sourceProperties']['name'] + " is: " + str(result) + " minutes....")
                      sys.exit(6)
                  else:
                    # Check dryrun flag and skip the rest of checks
                    if dryrun == "Yes":
                       machine_status += 1
                    else:
                       # Check if the target machine has been tested already
                        if launchtype == "test":
                            if 'lastTestLaunchDateTime' not in machine["lifeCycle"] and 'lastCutoverDateTime' not in machine["lifeCycle"]:
                                machine_status += 1
                            else:
                                print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has been tested already....")
                                sys.exit(2)
                        # Check if the target machine has been migrated to PROD already
                        elif launchtype == "cutover":
                            if 'lastTestLaunchDateTime' in machine["lifeCycle"]:
                                if 'lastCutoverDateTime' not in machine["lifeCycle"]:
                                    machine_status += 1
                                else:
                                    print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has been migrated already....")
                                    sys.exit(3)
                            else:
                                print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has not been tested....")
                                sys.exit(4)
        if machine_exist == False:
               print("ERROR: Machine: " + config[index]["machineName"] + " does not exist....")
               sys.exit(7)

    if machine_status == config["project"]["machinecount"]:
       print("All Machines in the config file are ready....")
    else:
       print("ERROR: some machines in the config file are not ready....")
       sys.exit(5)