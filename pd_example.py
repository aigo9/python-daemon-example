#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import time
import argparse
import logging
import daemon
import signal

from pidlockfile import PIDLockFile

def do_some_work(args):

    logger = logging.getLogger(args.daemon_name)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(args.log_file)
    fh.setLevel(logging.INFO)

    log_format = '%(asctime)s|%(levelname)s|%(message)s'

    fh.setFormatter(logging.Formatter(log_format))

    logger.addHandler(fh)

    while True:
        logger.info("sample INFO message")
        time.sleep(5)


def f_start(args):
    if args.verbose:
        print("{0}: starting...".format(args.daemon_name))
        print("{0}: pid_file = {1}".format(args.daemon_name, args.pid_file))
        print("{0}: log_file = {1}".format(args.daemon_name, args.log_file))

    with daemon.DaemonContext(
        working_directory=args.working_directory,
        umask=0o002,
        pidfile=PIDLockFile(args.pid_file, timeout=2.0),
        stdout=open(args.stdout_file, "a", 0),
        stderr=open(args.stderr_file, "a", 0)):
        do_some_work(args)

def f_stop(args):
    if args.verbose:
        print("{0}: stopping...".format(args.daemon_name))

    plf = PIDLockFile(args.pid_file)
    pid = plf.is_locked()
    if pid:
        os.kill(pid, signal.SIGTERM)
    else:
        print("{0}: NOT running".format(args.daemon_name))

def f_restart(args):
    f_stop(args)
    f_start(args)

def f_status(args):
    plf = PIDLockFile(args.pid_file)
    pid = plf.is_locked()
    if pid:
        print("{0}: running, PID = {1}".format(args.daemon_name, pid))
    else:
        print("{0}: NOT running".format(args.daemon_name))

if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))
    base_name = os.path.basename(__file__).split('.')[0]

    # To avoid dealing with permissions and to simplify this example
    # setting working directory, pid file and log file location etc.
    # to the directory where the script is located. Normally these files
    # go to various subdirectories of /var

    # working directory, normally /var/lib/<daemon_name>
    working_directory = here

    # log file, normally /var/log/<daemon_name>.log
    log_file = os.path.join(here, base_name + ".log")

    # pid lock file, normally /var/run/<daemon_name>.pid
    pid_file = os.path.join(here, base_name + ".pid")

    # stdout, normally /var/log/<daemon_name>.stdout
    stdout_file = os.path.join(here, base_name + ".stdout")

    # stderr, normally /var/log/<daemon_name>.stderr
    stderr_file = os.path.join(here, base_name + ".stderr")

    parser = argparse.ArgumentParser(
        description="Minimalistic example of using python-daemon with pidlockfile"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="print additional messages to stdout",
        action="store_true"
    )
    parser.set_defaults(working_directory=working_directory)
    parser.set_defaults(log_file=log_file)
    parser.set_defaults(pid_file=pid_file)
    parser.set_defaults(stdout_file=stdout_file)
    parser.set_defaults(stderr_file=stderr_file)
    parser.set_defaults(daemon_name=base_name)
    subparsers = parser.add_subparsers(title="commands")
    sp_start = subparsers.add_parser("start", description="start daemon")
    sp_start.set_defaults(func=f_start)
    sp_stop = subparsers.add_parser("stop", description="stop daemon")
    sp_stop.set_defaults(func=f_stop)
    sp_restart = subparsers.add_parser("restart", description="restart daemon")
    sp_restart.set_defaults(func=f_restart)
    sp_status = subparsers.add_parser("status", description="check daemon status")
    sp_status.set_defaults(func=f_status)
    args = parser.parse_args()
    args.func(args)

