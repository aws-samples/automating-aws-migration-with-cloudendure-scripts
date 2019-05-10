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
import UpdateBlueprint
import CheckMachine
import LaunchMachine
import requests
import json

def execute(launchtype, session, headers, endpoint, HOST, projectname, configfile, dryrun):
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
        
        # Get Machine List
        m = requests.get(HOST + endpoint.format('projects/{}/machines').format(project_id), headers=headers, cookies=session)
        if "sourceProperties" not in m.text:
            print("ERROR: Failed to fetch the machines....")
            sys.exit(3)
        machinelist = {}
        for machine in json.loads(m.text)["items"]:
            print('Machine name:{}, Machine ID:{}'.format(machine['sourceProperties']['name'], machine['id']))
            machinelist[machine['id']] = machine['sourceProperties']['name']

        # Check Target Machines
        print("****************************")
        print("* Checking Target machines *")
        print("****************************")
        CheckMachine.status(session, headers, endpoint, HOST, project_id, configfile, launchtype, dryrun)
        
        # Update Machine Blueprint
        print("**********************")
        print("* Updating Blueprint *")
        print("**********************")
        UpdateBlueprint.update(launchtype, session, headers, endpoint, HOST, project_id, machinelist, configfile, dryrun)
        
        
        # Launch Target machines
        if dryrun == "No":
           print("*****************************")
           print("* Launching target machines *")
           print("*****************************")
           LaunchMachine.launch(launchtype, session, headers, endpoint, HOST, project_id, configfile)
        
    except:
        print(sys.exc_info())
        sys.exit(6)