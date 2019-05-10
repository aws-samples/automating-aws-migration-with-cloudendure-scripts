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

def launch(launchtype, session, headers, endpoint, HOST, project_id, configfile):
    if launchtype == "test" or launchtype == "cutover":
       with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
            config = yaml.load(ymlfile)
    m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
    for i in range(1, config["project"]["machinecount"]+1):
        index = "machine" + str(i)
        for machine in json.loads(m.text)["items"]:
            if config[index]["machineName"] == machine['sourceProperties']['name']:
                if launchtype == "test":
                   machine_data = {'items': [{"machineId": machine['id']}], "launchType": "TEST"}
                elif launchtype == "cutover":
                   machine_data = {'items': [{"machineId": machine['id']}], "launchType": "CUTOVER"}
                else:
                  print("ERROR: Invalid Launch Type....")
        result = requests.post(HOST + endpoint.format('projects/{}/launchMachines').format(project_id), data = json.dumps(machine_data), headers = headers, cookies = session)
        # Response code translate to message
        if result.status_code == 202:
            if launchtype == "test":
               print("Test Job created for machine " + config[index]["machineName"] + "....")
            if launchtype == "cutover":
               print("Cutover Job created for machine " + config[index]["machineName"] + "....")
        elif result.status_code == 409:
            print("ERROR: " + config[index]["machineName"] + " has Job In Progress....")
        elif result.status_code == 402:
            print("ERROR: Project license has expired....")
        else:
            print("ERROR: Launch target machine failed....")