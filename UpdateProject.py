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
import base64


def update(cloud_endure, projectname, configfile):
    project_id = cloud_endure.get_project_id(projectname)
    with open(os.path.join(sys.path[0], configfile), 'r') as ymlfile:
        config = yaml.load(ymlfile)
    # Update encryption key and replication server
    rep = cloud_endure.fetch_replication_conf(project_id)
    for replication in json.loads(rep.text)["items"]:
        replication["volumeEncryptionKey"] = config["replication"]["encryptionkey"]
        replication["volumeEncryptionAllowed"] = True
        replication["subnetId"] = config["replication"]["subnetID"]
        replication["replicatorSecurityGroupIDs"] = config["replication"]["securitygroupIDs"]
        cloud_endure.update_replication_conf(projectname, project_id, replication['id'], replication)
