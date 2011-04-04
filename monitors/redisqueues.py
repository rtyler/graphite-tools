#!/usr/bin/env python

import optparse
import os
import sys
import time

try:
    import simplejson as json
except ImportError:
    import json


def main():
    try:
        import redis
    except ImportError, ex:
        sys.stderr.write('redisqueues.py requires the `redis` module\n')
        return 1

    opts = optparse.OptionParser()
    opts.add_option('-p', '--prefix', dest='prefix',
                help='Specify a prefix for the event labels (e.g. foo.system.load)')
    opts.add_option('-s', '--suffix', dest='suffix',
                help='Specify a suffix for the event labels (e.g. system.load.1min.hostname')
    opts.add_option('--db', default=0, dest='db',
                help='Specify a redis DB to query')
    opts.add_option('--lists', dest='lists',
                help='Specify a comma-separated list of redis keys to get the length of')
    options, args = opts.parse_args()

    prefix = ''
    suffix = ''

    if options.prefix:
        prefix = '%s.' % options.prefix
    if options.suffix:
        suffix = '.%s' % options.suffix

    if not options.lists:
        sys.stderr.write('redisqueues.py requires the `--lists` parameter to properly report list lengths\n')
        return 1

    r = redis.Redis(host='localhost', port=6379, db=options.db)
    now = time.time()

    for queue in options.lists.split(','):
        try:
            value = r.llen(queue)
            print '%(prefix)ssystem.redis.%(queue)s.length%(suffix)s %(value)s %(now)s' % locals()
        except Exception, ex:
            sys.stderr.write('Exception when calling `r.llen` in redisqueues.py: %s\n' % ex)
    return 0

if __name__ == '__main__':
    sys.exit(main())

