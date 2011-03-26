#!/usr/bin/env python

import optparse
import os
import sys
import time

def main():
    proc_path = '/proc/loadavg'

    if not os.path.exists(proc_path):
        sys.stderr.write('load.py only supports systems with /proc\n')
        return 1

    opts = optparse.OptionParser()
    opts.add_option('-p', '--prefix', dest='prefix',
                help='Specify a prefix for the event labels (e.g. foo.system.load)')
    options, args = opts.parse_args()

    pieces = None

    with open(proc_path, 'r') as fd:
        buf = fd.read().strip()
        pieces = buf.split(' ')

    if not pieces or len(pieces) < 3:
        return 1

    one, five, fifteen = pieces[0], pieces[1], pieces[2]
    now = int(time.time())
    prefix = ''

    if options.prefix:
        prefix = '%s.' % options.prefix

    print '%(prefix)ssystem.load.1min %(one)s %(now)s' % locals()
    print '%(prefix)ssystem.load.5min %(five)s %(now)s' % locals()
    print '%(prefix)ssystem.load.15min %(fifteen)s %(now)s' % locals()

    return 0

if __name__ == '__main__':
    sys.exit(main())

