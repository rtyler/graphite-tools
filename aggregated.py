#!/usr/bin/env python
"""
    Copyright (C) 2011 Apture, Inc

    Author: R. Tyler Croy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN

"""

import optparse
import sys

import eventlet
eventlet.monkey_patch()

from eventlet.green import time
from eventlet.green import socket
from eventlet.green import SocketServer

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003
AGGREGATE_TIMEOUT = 60

class StatsServer(SocketServer.UDPServer):
    debug = False
    def __init__(self, *args, **kwargs):
        self._count_data = {}
        self._timing_data = {}
        eventlet.spawn_after(AGGREGATE_TIMEOUT, self.aggregate_flush)
        SocketServer.UDPServer.__init__(self, *args, **kwargs)

    def _generate_counts(self):
        for label, points in self._count_data.iteritems():
            value = 0.0
            for count, tstamp in points:
                value += float(count)
            now = int(time.time())
            yield '%(label)s %(value)s %(now)s' % locals()

    def _generate_timings(self):
        for label, points in self._timing_data.iteritems():
            lower = sys.maxint
            upper = 0.0
            total = 0.0
            count = 0.0
            for delta, tstamp in points:
                if delta < lower:
                    lower = delta
                if delta > upper:
                    upper = delta
                count += 1.0
                total += delta
            now = int(time.time())
            average = (total / count)

            yield '%(label)s.avg %(average)s %(now)s' % locals()
            yield '%(label)s.lower %(lower)s %(now)s' % locals()
            yield '%(label)s.upper %(upper)s %(now)s' % locals()
            yield '%(label)s.count %(count)s %(now)s' % locals()

    def _clear_data(self):
        for d in (self._count_data, self._timing_data):
            for key in d.keys():
                del d[key]

    def aggregate_flush(self):
        try:
            if not self._count_data and not self._timing_data:
                return

            counts = '\n'.join(self._generate_counts()) + '\n'
            timings = '\n'.join(self._generate_timings()) + '\n'

            if self.debug:
                if self._count_data:
                    print 'writing counts:'
                    print repr(counts)
                if self._timing_data:
                    print 'writing timings:'
                    print repr(timings)

            csock = socket.socket()
            csock.connect((CARBON_SERVER, CARBON_PORT,))
            try:
                csock.sendall(counts)
                csock.sendall(timings)
            finally:
                csock.close()
                self._clear_data()
        finally:
            eventlet.spawn_after(AGGREGATE_TIMEOUT, self.aggregate_flush)

class StatsHandler(SocketServer.DatagramRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        if not data:
            return

        chunks = data.split(' ')
        if not len(chunks) == 3:
            return

        label, value, tstamp = chunks[0], chunks[1], float(chunks[2])

        if self.server.debug:
            print '<<handle>> %s %s %s' % (label, value, tstamp)

        stats = self.server._count_data
        # values of "1235|s" are to be consider *timings* instead of counts
        if value[-2:] == '|s':
            stats = self.server._timing_data
            value = value[:-2]

        value = float(value)

        if not stats.has_key(label):
            stats[label] = []

        stats[label].append((value, tstamp))

class DebugStatsServer(StatsServer):
    debug = True

def main():
    options = optparse.OptionParser()
    options.add_option('-d', '--debug', action='store_true',
                    dest='debug', help='Turn on aggregated debug statements')
    opts, args = options.parse_args()
    klass = StatsServer

    if opts.debug:
        klass = DebugStatsServer


    server = klass(('', 22034,), StatsHandler)
    print '>> Starting server on port 22034'
    print
    server.serve_forever()
    return 0

if __name__ == '__main__':
    sys.exit(main())

