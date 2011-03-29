#!/usr/bin/env python

import optparse
import os
import sys
import time

KEYS_BLACKLIST = ('version', 'time', 'pid',
                'pointer_size', 'limit_maxbytes',
                'uptime',)

def main():
    try:
        import memcache
    except ImportError, ex:
        sys.stderr.write('memcached.py requires the `memcache` module\n')
        return 1

    opts = optparse.OptionParser()
    opts.add_option('-p', '--prefix', dest='prefix',
                help='Specify a prefix for the event labels (e.g. foo.system.load)')
    opts.add_option('-s', '--suffix', dest='suffix',
                help='Specify a suffix for the event labels (e.g. system.load.1min.hostname')
    options, args = opts.parse_args()

    prefix = ''
    suffix = ''

    if options.prefix:
        prefix = '%s.' % options.prefix
    if options.suffix:
        suffix = '.%s' % options.suffix

    m = memcache.Client(('localhost:11211',))
    now = time.time()

    try:
        stats = m.get_stats()
    except Exception, ex:
        sys.stderr.write('Exception when getting stats: %s\n' % ex)
        return 1

    for host, data in stats:
        for key, value in data.iteritems():
            if key in KEYS_BLACKLIST:
                continue
            print '%(prefix)ssystem.memcached.%(key)s%(suffix)s %(value)s %(now)s' % locals()

    return 0

if __name__ == '__main__':
    sys.exit(main())

