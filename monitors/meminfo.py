#!/usr/bin/env python

import optparse
import os
import sys
import time

def main():
    proc_path = '/proc/meminfo'

    if not os.path.exists(proc_path):
        sys.stderr.write('meminfo.py only supports systems with /proc\n')
        return 1

    opts = optparse.OptionParser()
    opts.add_option('-p', '--prefix', dest='prefix',
                help='Specify a prefix for the event labels (e.g. foo.system.load)')
    options, args = opts.parse_args()

    pieces = None

    with open(proc_path, 'r') as fd:
        buf = fd.read().strip()
        pieces = buf.split('\n')

    prefix = ''
    now = int(time.time())

    if options.prefix:
        prefix = '%s.' % options.prefix

    for piece in pieces:
        if not piece.endswith('kB'):
            continue

        parts = piece.split(':')

        if not len(parts) == 2:
            continue

        label = parts[0].lower()
        value = parts[1].strip()
        # Trim the " kB" suffix
        value = value[:-3]
        print '%(prefix)ssystem.meminfo.%(label)s %(value)s %(now)s' % locals()


    return 0

if __name__ == '__main__':
    sys.exit(main())

