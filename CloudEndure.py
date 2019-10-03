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
import argparse
import Machine
import UpdateProject
import requests
import json
import StatusCheck
import Cleanup
import os
import CloudEndure_manager


def is_file(file_name):
    if not os.path.isfile(file_name):
        raise argparse.ArgumentTypeError
    return file_name


def init(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--projectname', required=True)
    parser.add_argument('-u', '--userapitoken', required=True)
    parser.add_argument('-d', '--dryrun', action='store_true', default=False)
    parser.add_argument('-c', '--config', default='./config-test.yml', type=is_file, help='YML config file')

    subparsers = parser.add_subparsers(help='List of actions to perform with CloudEndure...', dest='command')

    # Create parser for GetBlueprint
    blueprint = subparsers.add_parser('blueprint', help='Act over Machine Blueprint in CloudEndure...')
    blueprint.add_argument('-d', '--do', choices=['get', 'update'], help='Choose the action to do over blueprint')

    subparsers.add_parser('project-update', help='Act over project configuration...')

    launch = subparsers.add_parser('launch', help='Launch machines to be replicated in the cloud.')
    launch.add_argument('-t', '--type', choices=['test', 'cutover'], required=True)

    subparsers.add_parser('clean', help='Cleanup...')

    check = subparsers.add_parser('check-status', help='Perform Status checking...')
    check.add_argument('-t', '--type', choices=['test', 'cutover'], required=True)

    args = parser.parse_args(arguments)
    return args


def main(arguments):
    args = init(arguments)

    print("************************")
    print("* Login to CloudEndure *")
    print("************************")
    cloud_endure = CloudEndure_manager.CloudEndure()
    cloud_endure.login(args.userapitoken)

    if args.command == "blueprint":
        if args.do == "get":
            pass
        elif args.do == "update":
            pass
    elif args.command == "project-update":
        UpdateProject.update(cloud_endure, args.projectname, args.config)
        sys.exit(4)
    elif args.command == "clean":
        Cleanup.remove(cloud_endure, args.projectname, args.config, args.dryrun)
        sys.exit(2)
    elif args.command == 'launch':
        Machine.execute(args.type, cloud_endure, args.projectname, args.config, args.dryrun)
    elif args.command == 'check-status':
        StatusCheck.check(args.type, cloud_endure, args.projectname, args.config)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
