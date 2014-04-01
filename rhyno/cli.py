#! /usr/bin/env python

import os
import argparse
from api import *
import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logging.getLogger('').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

STAGE_HOST = "http://stage.plosjournals.org/api/v1/"
PRODUCTION_HOST = "http://api.plosjournals.org/v1/"

def get_rhyno(production):
    if production:
        r = Rhyno(PRODUCTION_HOST)
    else:
        r = Rhyno(STAGE_HOST)
    return r

def publish(args):
    r = get_rhyno(args.production)
    if args.syndicate:
        r.production_publish(args.doi)
    else:
        r.publish(args.doi)

def unpublish(args):
    r = get_rhyno(args.production)
    r.unpublish(args.doi)

def ingest(args):
    r = get_rhyno(args.production)
    r.ingest(args.file, force_reingest=args.force)

def parse_call():
    desc = """
    CLI-based rhino tools for manupulating articles in ambra
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-p', '--production', action="store_true", help="use production rhino (defaults to stage)")
    parser.add_argument('-l', '--logging-level', nargs=1, help="logging level (defaults to ERROR",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    subparsers = parser.add_subparsers(help='action dispatcher: define an action to run')

    # publish
    parser_publish = subparsers.add_parser('publish',
                                           help="publish an article")
    parser_publish.add_argument('-s', '--syndicate', action="store_true", help="also syndicates article to all sources")
    parser_publish.add_argument('doi',
                                help="article doi")
    parser_publish.set_defaults(func=publish)

    # publish
    parser_unpublish = subparsers.add_parser('unpublish',
                                           help="unpublish an article")
    parser_unpublish.add_argument('doi',
                                help="article doi")
    parser_unpublish.set_defaults(func=unpublish)

    # ingest
    parser_ingest = subparsers.add_parser('ingest',
                                          help="ingest an article")
    parser_ingest.add_argument('-f', '--force', action="store_true", help="force ingest")
    parser_ingest.add_argument('file',
                               help="article archive file")
    parser_ingest.set_defaults(func=ingest)


    args = parser.parse_args()
    if args.logging_level:
        logging.getLogger('').setLevel(getattr(logging, args.logging_level[0]))

    args.func(args)

if __name__ == "__main__":
    parse_call()
