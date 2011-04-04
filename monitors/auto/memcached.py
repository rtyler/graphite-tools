#!/usr/bin/env python

import optparse
import os
import sys
import time

try:
    import simplejson as json
except ImportError:
    import json


KEYS_BLACKLIST = ('version', 'time', 'pid',
                'pointer_size', 'limit_maxbytes',
                'connection_structures',
                'listen_disable_num',
                'uptime',)
STATE_FILE = '/tmp/memcached_graphite_state'

RATES = ('auth_cmds', 'auth_errors', 'bytes_read', 'bytes_written',
            'cas_badval', 'cas_hits', 'cas_misses', 'cas_flush', 'cmd_get',
            'cmd_set', 'decr_hits', 'decr_misses', 'delete_hits', 'delete_misses',
            'evictions', 'get_hits', 'get_misses', 'incr_hits', 'incr_misses',)

def write_state(state):
    with open(STATE_FILE, 'w') as fd:
        buffer = {'time' : int(time.time()), 'data' : state}
        fd.write(json.dumps(buffer))

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

    if not stats:
        return 0

    stats = stats[0][1]

    # If we don't have a state file, just exit and we'll record some rates next
    # time around
    if not os.path.exists(STATE_FILE):
        write_state(stats)
        return 0

    stored = {}
    with open(STATE_FILE, 'r') as fd:
        stored = json.loads(fd.read())

    # Once we've read our previous state, best to flush our current state
    write_state(stats)

    if not stored:
        return 0

    if not stored.get('time') or not stored.get('data'):
        return 0

    # If we've made it to this point, we have a *valid( state file read into
    # `stored` and we actually have some `stats` to report on a delta with.

    time_diff = float(time.time() - stored['time'])

    for key, value in stats.iteritems():
        if key in KEYS_BLACKLIST:
            continue

        if not stored['data'].get(key):
            continue

        if key in RATES:
            value = float( (float(value) - float(stored['data'][key])) / time_diff)
            key = '%s_per_sec' % key

        print '%(prefix)ssystem.memcached.%(key)s%(suffix)s %(value)s %(now)s' % locals()

    return 0

if __name__ == '__main__':
    sys.exit(main())

