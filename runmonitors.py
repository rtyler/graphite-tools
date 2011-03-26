#!/usr/bin/env python

import glob
import optparse
import socket
import subprocess
import sys

def main():
    options = optparse.OptionParser()
    options.add_option('-p', '--port', default=2003, dest='port',
                        help='Define the port where Carbon is running')
    options.add_option('--host', default='127.0.0.1', dest='host',
                        help='Define the host where Carbon is running')
    options.add_option('--prefix', dest='prefix',
                        help='Prefix to pass along to all monitors (to prefix the label in Graphite)')

    opts, args = options.parse_args()

    args = []
    if opts.prefix:
        args = ['-p', opts.prefix]

    messages = []
    for f in glob.iglob('monitors/*'):
        p = subprocess.Popen([sys.executable, f] + args, stdout=subprocess.PIPE)
        out, err = p.communicate()
        messages.extend([r.strip() for r in out.split('\n') if r])

    packet = '\n'.join(messages) + '\n'

    sock = socket.socket()
    sock.connect((opts.host, opts.port))
    sock.sendall(packet)
    sock.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())

