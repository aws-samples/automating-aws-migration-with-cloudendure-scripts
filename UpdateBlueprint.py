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

def update(launchtype, session, headers, endpoint, HOST, projectId, machinelist, configfile, dryrun):
    if launchtype == "test" or launchtype == "cutover":
       with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
            config = yaml.safe_load(ymlfile)
    else:
       print("Invalid Launch Type !")
    try:
        b = requests.get(HOST + endpoint.format('projects/{}/blueprints').format(projectId), headers=headers, cookies=session)
        for blueprint in json.loads(b.text)["items"]:
            machineName = machinelist[blueprint["machineId"]]
            for i in range(1, config["project"]["machinecount"]+1):
                index = "machine" + str(i)
                if config[index]["machineName"] == machineName:
                    url = endpoint.format('projects/{}/blueprints/').format(projectId) + blueprint['id']
                    blueprint["instanceType"] = config[index]["instanceType"]
                    blueprint["tenancy"] = config[index]["tenancy"]
                    if config[index]["iamRole"].lower() != "none":
                        blueprint["iamRole"] = config[index]["iamRole"]
                    for disk in blueprint["disks"]:
                           blueprint["disks"] = [{"type":"SSD", "name":disk["name"]}]
                    existing_subnetId = blueprint["subnetIDs"]
                    existing_SecurityGroupIds = blueprint["securityGroupIDs"]
                    blueprint["subnetIDs"] = config[index]["subnetIDs"]
                    blueprint["securityGroupIDs"] = config[index]["securitygroupIDs"]
                    blueprint["publicIPAction"] = 'DONT_ALLOCATE'
                    blueprint["privateIPAction"] = 'CREATE_NEW'
                    tags = []
                    # Update machine tags
                    for i in range(1, config[index]["tags"]["count"]+1):
                        keytag = "key" + str(i)
                        valuetag = "value" + str(i)
                        tag = {"key":config[index]["tags"][keytag], "value":config[index]["tags"][valuetag]}
                        tags.append(tag)
                    existing_tag = blueprint["tags"]
                    blueprint["tags"] = tags
                    result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers, cookies=session)
                    if result.status_code != 200:
                        print("ERROR: Updating blueprint failed for machine: " + machineName +", invalid blueprint config....")
                        if dryrun == "Yes":
                           print("ERROR: YAML validation failed, please fix the errors in the cutover YAML file")
                        sys.exit(4)
                    machinelist[blueprint["machineId"]] = "updated"
                    print("Blueprint for machine: " + machineName + " updated....")
                    if dryrun == "Yes":
                       blueprint["subnetIDs"] = existing_subnetId
                       blueprint["securityGroupIDs"] = existing_SecurityGroupIds
                       blueprint["tags"] = existing_tag
                       result = requests.patch(HOST + url, data=json.dumps(blueprint), headers=headers, cookies=session)
                       if result.status_code != 200:
                          print("ERROR: Failed to roll back subnet,SG and tags for machine: " + machineName +"....")
                          sys.exit(5)
                       else:
                          print("Dryrun was successful for machine: " + machineName +"...." )

    except:
        print("ERROR: Updating blueprint task failed....")
        print(sys.exc_info())
        sys.exit(3)