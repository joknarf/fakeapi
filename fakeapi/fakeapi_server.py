#!/usr/bin/env python

""" start fakeapi http server """
import argparse
from fakeapi import FakeAPI

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", type=str, default='localhost',
                    help="HTTP server address")
parser.add_argument("-p", "--port", type=int, default=8080,
                    help="HTTP server port")
parser.add_argument("-P", "--prefix", type=str, default=None,
                    help="HTTP prefix (http://server:port)")
parser.add_argument("jsonfile", type=str, default='-', nargs='?',
                    help="Json file for FakeAPI")

args = parser.parse_args()

api = FakeAPI(url_json=args.jsonfile)
api.http_server(args.server, args.port, args.prefix)
