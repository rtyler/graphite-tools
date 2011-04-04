#!/usr/bin/env python

import glob
import optparse
import socket
import subprocess
import sys


def run_monitor(filename, args):
    p = subprocess.Popen([sys.executable, filename] + args, stdout=subprocess.PIPE)
    out, err = p.communicate()
    return [r.strip() for r in out.split('\n') if r]


def main():
    options = optparse.OptionParser()
    options.add_option('-p', '--port', default=2003, dest='port',
                        help='Define the port where Carbon is running')
    options.add_option('-d', '--debug', dest='debug', action='store_true',
                        help='Switch runmonitors.py into debug mode, which prevents it from connecting to Carbon')
    options.add_option('--host', default='127.0.0.1', dest='host',
                        help='Define the host where Carbon is running')
    options.add_option('--prefix', dest='prefix',
                        help='Prefix to pass along to all monitors (to prefix the label in Graphite)')
    options.add_option('--suffix', dest='suffix',
                        help='Suffix for all monitors, useful for identifying the machine')
    options.add_option('-f', '--file', default=None, dest='file',
                        help='Run a specific monitor file')
    options.add_option('--opts', dest='fopts',
                        help='Options string to pass to the monitor being executed')

    opts, args = options.parse_args()

    args = []
    if opts.prefix:
        args = ['-p', opts.prefix]
    if opts.suffix:
        args = args + ['-s', opts.suffix]

    if opts.fopts:
        args = args + opts.fopts.split(' ')

    messages = []

    if opts.file:
        messages.extend(run_monitor(opts.file, args))
    else:
        for f in glob.iglob('monitors/auto/*'):
            messages.extend(run_monitor(f, args))

    if opts.debug:
        for m in messages:
            print m
        return 0

    packet = '\n'.join(messages) + '\n'

    sock = socket.socket()
    sock.connect((opts.host, opts.port))
    sock.sendall(packet)
    sock.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())

