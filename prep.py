#!/usr/bin/env python
from pprint import pprint
import subprocess
import argparse
import json
import os

class Msg(object):
    """
    Helper for printing text using ANSI[1] escape code
    [1] https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    RESET = '\033[0m'
    BOLD = '\033[1m'
    FAINT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    RED_HI = '\033[91m'
    GREEN_HI = '\033[92m'
    YELLOW_HI = '\033[93m'
    BLUE_HI = '\033[94m'
    PURPLE_HI = '\033[95m'

    def __init__(self):
        pass

    @staticmethod
    def info(*msgs):
        """Print an informational message."""
        print " ".join(msgs)

    @staticmethod
    def emph(*msgs):
        """Print an emphasized message."""
        head, tail = msgs[0], " " + " ".join(msgs[1:]) if msgs[1:] else ""
        print Msg.BOLD + Msg.BLUE_HI + "** "+ head +" **"+ Msg.RESET + tail

    @staticmethod
    def good(*msgs):
        """Print an green/good message."""
        head, tail = msgs[0], " " + " ".join(msgs[1:]) if msgs[1:] else ""
        print Msg.GREEN_HI + head + Msg.RESET + tail

    @staticmethod
    def warn(*msgs):
        """Print a YELLOW_HI message."""
        head, tail = msgs[0], " " + " ".join(msgs[1:]) if msgs[1:] else ""
        print Msg.YELLOW_HI + head + Msg.RESET + tail

    @staticmethod
    def fail(*msgs):
        """Print a failure message."""
        head, tail = msgs[0], " " + " ".join(msgs[1:]) if msgs[1:] else ""
        print Msg.RED_HI + head + Msg.RESET + tail

def prompt(msg=None):
    """Prompt the user for confirmation, choises: [Yes/No/All]"""

    if msg is None:
        msg = "Are you sure? [Yes|No|All] "
        
    response = raw_input(msg).lower().strip()
    confirmed_all = response != "" and response[0] == "a"
    confirmed = confirmed_all or response == "" or response[0] == "y"

    return confirmed, confirmed_all

def cmd_prep(options):
    """Setup workspace: clone repos and switch branch."""

    workspace = options["workspace"]
    env = options["env"]

    if (os.path.exists(workspace)):
        Msg.warn("Workspace(%s) exists." % workspace)
    else:
        os.mkdir(options["workspace"])                  # Create the workspace dir

    for repos in env["repos"]:                          # Clone repos
        dst = os.sep.join([workspace, repos["alias"]])
        if not os.path.exists(dst):
            Msg.emph("Repos(%s) - cloning" % repos["alias"])
            process = subprocess.Popen(
                ['git', 'clone', repos["url"], dst]
            )
            out, err = process.communicate()
            if out:
                print out
            if err:
                Msg.fail(err)

        Msg.emph("Repos(%s) - branching to '%s'" % (repos["alias"], repos["branch"]))
        process = subprocess.Popen(
            ['git', 'checkout', repos["branch"]],
            cwd=dst
        )
        out, err = process.communicate()
        if out:
            print out
        if err:
            Msg.fail(err)

def main():

    ENVS = json.load(open('envs.json'))     # Grab environments
    DEFAULT_ENV = ENVS[0]

    parser = argparse.ArgumentParser(description='Environment setup and invocation')
    parser.add_argument(
        'name',
        choices=[env["name"] for env in ENVS],
        default=DEFAULT_ENV,
        help='The environment to setup (default: %(default))'
    )
    parser.add_argument(
        'workspace',
        help='Path to repository folder'
    )
    args = parser.parse_args()

    options = {
        "workspace": os.sep.join([
            os.path.abspath(args.workspace), args.name
        ]),
        "env": [env for env in ENVS if env["name"] == args.name][0]
    }
    cmd_prep(options)

    json.dump(ENVS, open('envs.json', 'w'), indent=2)

if __name__ == "__main__":
    main()
