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
import argparse
import Machine
import UpdateProject
import requests
import json
import StatusCheck
import Cleanup

HOST = 'https://console.cloudendure.com'
headers = {'Content-Type': 'application/json'}
session = {}
endpoint = '/api/latest/{}'

def login(userapitoken, endpoint):
    login_data = {'userApiToken': userapitoken}
    r = requests.post(HOST + endpoint.format('login'),
                  data=json.dumps(login_data), headers=headers)
    if r.status_code != 200 and r.status_code != 307:
        if r.status_code == 401:
            print("ERROR: The login credentials provided cannot be authenticated....")
        elif r.status_code == 402:
            print("ERROR: There is no active license configured for this account....")
        elif r.status_code == 429:
            print("ERROR: Authentication failure limit has been reached. The service will become available for additional requests after a timeout....")
        sys.exit(1)

    # check if need to use a different API entry point
    if r.history:
        endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
        r = requests.post(HOST + endpoint.format('login'),
                      data=json.dumps(login_data), headers=headers)
                      
    session['session'] = r.cookies['session']
    try:
       headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']
    except:
       pass

def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--userapitoken', required=True)
    parser.add_argument('--configfile', required=True)
    parser.add_argument('--launchtype')
    parser.add_argument('--projectname', required=True)
    parser.add_argument('--updateproject', default="No")
    parser.add_argument('--statuscheck', default="No")
    parser.add_argument('--cleanup', default="No")
    parser.add_argument('--dryrun', default="No")
    args = parser.parse_args(arguments)
    
    print("************************")
    print("* Login to CloudEndure *")
    print("************************")
    login(args.userapitoken, endpoint)

        
    if args.updateproject == "Yes":
       UpdateProject.update(session, headers, endpoint, HOST, args.projectname, args.configfile)
       sys.exit(4)
    
    if args.cleanup == "Yes":
       Cleanup.remove(session, headers, endpoint, HOST, args.projectname, args.configfile)
       sys.exit(2)
    
    if args.dryrun != "No" and args.dryrun != "Yes":
        print("ERROR: Please type '--dryrun Yes' if you want to validate your production YAML file....")
        sys.exit(3)
    
    if args.launchtype == "test" or args.launchtype =="cutover":
           if args.statuscheck == "No":
               Machine.execute(args.launchtype, session, headers, endpoint, HOST, args.projectname, args.configfile, args.dryrun)
           else:
               if args.statuscheck =="Yes":
                   StatusCheck.check(args.launchtype, session, headers, endpoint, HOST, args.projectname, args.configfile)
               else:
                   print("ERROR: Please type '--statuscheck Yes' if you want to check migration status....")
    else:
           print("ERROR: Please use the valid launch type: test|cutover....")
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))