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

def remove(session, headers, endpoint, HOST, projectname, configfile):
    with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
        config = yaml.safe_load(ymlfile)
    
    # Get Projects
    r = requests.get(HOST + endpoint.format('projects'), headers=headers, cookies=session)
    if r.status_code != 200:
        print("ERROR: Failed to fetch the project....")
        sys.exit(1)
    try:
        # Get Project ID
        projects = json.loads(r.text)["items"]
        project_exist = False
        for project in projects:
            if project["name"] == projectname:
               project_id = project["id"]
               project_exist = True
        if project_exist == False:
            print("ERROR: Project Name does not exist....")
            sys.exit(2)
    except:
        print(sys.exc_info())
        sys.exit(6)

    m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
    machine_status = 0
    for i in range(1, config["project"]["machinecount"]+1):
        index = "machine" + str(i)
        machine_exist = False
        for machine in json.loads(m.text)["items"]:
           if config[index]["machineName"] == machine['sourceProperties']['name']:
                  machine_exist = True
                  if 'lastCutoverDateTime' in machine["lifeCycle"]:
                      machine_data = {'machineIDs': [machine['id']]}
                      remove = requests.delete(HOST + endpoint.format('projects/{}/machines').format(project_id), data = json.dumps(machine_data), headers=headers, cookies=session)
                      if remove.status_code == 204:
                          print("Machine: " + machine['sourceProperties']['name'] + " has been removed from CloudEndure....")
                          machine_status += 1
                      else:
                          print("Machine: " + machine['sourceProperties']['name'] + " cleanup failed....")
                  else:
                      print("ERROR: Machine: " + machine['sourceProperties']['name'] + " has not been migrated to PROD environment....")
                      sys.exit(4)
        if machine_exist == False:
               print("ERROR: Machine: " + config[index]["machineName"] + " does not exist....")

    if machine_status == config["project"]["machinecount"]:
       print("All Machines in the config file have been removed from CloudEndure....")
    else:
       print("ERROR: Some machines in the config file do not exist or have NOT been migrated to the PROD environment....")
       sys.exit(5)