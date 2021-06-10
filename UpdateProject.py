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
import base64

def update(session, headers, endpoint, HOST, projectname, configfile):
    with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
            config = yaml.safe_load(ymlfile)
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
        
        # Update encryption key and replication server
        rep = requests.get(HOST + endpoint.format('projects/{}/replicationConfigurations').format(project_id), headers=headers, cookies=session)
        for replication in json.loads(rep.text)["items"]:
            url = endpoint.format('projects/{}/replicationConfigurations/').format(project_id) + replication['id']
            replication["volumeEncryptionKey"] = config["replication"]["encryptionkey"]
            replication["volumeEncryptionAllowed"] = True
            replication["subnetId"] = config["replication"]["subnetID"]
            replication["replicatorSecurityGroupIDs"] = config["replication"]["securitygroupIDs"]
            eresult = requests.patch(HOST + url, data=json.dumps(replication), headers=headers, cookies=session)
            if eresult.status_code == 200:
               print("Encryption Key and replication server updated for project: " + projectname + "....")
            else:
               print("ERROR: Updating Encryption key or replication server failed....")

    except:
        print("ERROR: Updating project failed....")
        print(sys.exc_info())
        sys.exit(3)