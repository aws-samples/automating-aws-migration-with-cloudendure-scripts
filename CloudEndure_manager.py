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


import requests
import json


class ProjectError(Exception):
    """"Project exception to handle request errors gracefully
    Attributes:
            message -- Explanation of the error
    """

    def __init__(self, message=None):
        self.message = "Project information is not available.\n"
        if message is not None:
            self.message += message


class CloudEndure:
    def __init__(self):
        self.session = {}
        self.headers = {'Content-Type': 'application/json'}
        self.endpoint = '/api/latest/{}'
        self.project_endpoint = 'projects'
        self.login_endpoint = 'login'
        self.replication_endpoint = "projects/{}/replicationConfigurations"
        self.host = 'https://console.cloudendure.com'

    def fetch_project(self):
        try:
            project_info = requests.get(self.host + self.endpoint.format(self.project_endpoint),
                                        headers=self.headers,
                                        cookies=self.session)
        except requests.exceptions.RequestException as e:
            raise ProjectError("Failed to fetch the project...")

        return project_info

    def get_machine_list(self, project_id):
        try:
            machines = requests.get(self.host + self.endpoint.format('projects/{}/machines').format(project_id),
                                    headers=self.headers, cookies=self.session)
        except requests.exceptions.RequestException as e:
            raise ProjectError("Failed to fetch the machines...")
        machines_info = {machines['sourceProperties']['name']: machines for machines in
                         json.loads(machines.text)["items"]}
        return machines_info

    def fetch_replication_conf(self, project_id):
        try:
            repliaction_info = requests.get(
                self.host + self.endpoint.format('projects/{}/replicationConfigurations').format(project_id),
                headers=self.headers, cookies=self.session)
        except requests.exceptions.RequestException as e:
            raise ProjectError("Failed to fetch replication configurations...")
        return repliaction_info

    def update_replication_conf(self, projectname, project_id, replication_id, replication):
        url = self.endpoint.format('projects/{}/replicationConfigurations/').format(project_id) + replication_id
        try:
            eresult = requests.patch(self.host + url, data=json.dumps(replication), headers=self.headers,
                                     cookies=self.session)
            print("Encryption Key and replication server updated for project: " + projectname + "....")
        except requests.exceptions.RequestException as e:
            raise ("ERROR: Updating Encryption key or replication server failed....")
        return eresult

    def remove_machine(self, name, project_id, machine_data):
        status = False
        remove = requests.delete(self.host + self.endpoint.format('projects/{}/machines').format(project_id),
                                 data=json.dumps(machine_data), headers=self.headers, cookies=self.session)
        if remove.status_code == 204:
            print("Machine: " + machine['sourceProperties']['name'] + " has been removed from CloudEndure....")
            status = True
        else:
            print("Machine: " + machine['sourceProperties']['name'] + " cleanup failed....")
        return status

    def login(self, userapitoken):
        login_data = {'userApiToken': userapitoken}
        r = requests.post(self.host + self.endpoint.format(self.login_endpoint),
                          data=json.dumps(login_data), headers=self.headers)
        if r.status_code != 200 and r.status_code != 307:
            if r.status_code == 401:
                raise ProjectError("ERROR: The login credentials provided cannot be authenticated....")
            elif r.status_code == 402:
                raise ProjectError("ERROR: There is no active license configured for this account....")
            elif r.status_code == 429:
                raise ProjectError("ERROR: Authentication failure limit has been reached. The service will become"
                                   " available for additional requests after a timeout....")

        # check if need to use a different API entry point
        if r.history:
            endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
            r = requests.post(self.host + endpoint.format(self.login_endpoint),
                              data=json.dumps(login_data), headers=self.headers)

        self.session['session'] = r.cookies['session']
        self.headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']

    def get_project_id(self, project_name):
        r = self.fetch_project()
        try:
            # Get Project ID
            projects = {project['name']: project['id'] for project in json.loads(r.text)["items"]}
            if project_name in projects.keys():
                project_id = projects[project_name]
            else:
                raise ProjectError("ERROR: Project Name does not exist....")
                # print("ERROR: Project Name does not exist....")
                # sys.exit(2)
        except:
            raise ProjectError("ERROR: Retrieved project data is malformed or empty, please try again")
            # sys.exit(6)
        return project_id
