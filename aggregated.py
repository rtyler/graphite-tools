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
    def __init__(self, *args, **kwargs):
        self._stats_data = {}
        eventlet.spawn_after(AGGREGATE_TIMEOUT, self.aggregate_flush)
        SocketServer.UDPServer.__init__(self, *args, **kwargs)

    def aggregate_flush(self):
        try:
            if not self._stats_data:
                return

            events = []

            for label, points in self._stats_data.iteritems():
                value = 0.0
                for count, tstamp in points:
                    value += float(count)
                now = int(time.time())
                events.append('%(label)s %(value)s %(now)s' % locals())

            for key in self._stats_data.keys():
                del self._stats_data[key]

            message = '\n'.join(events) + '\n'
            csock = socket.socket()
            csock.connect((CARBON_SERVER, CARBON_PORT,))
            try:
                csock.sendall(message)
            finally:
                csock.close()
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

        label, value, tstamp = chunks[0], float(chunks[1]), float(chunks[2])

        stats = self.server._stats_data
        if not stats.has_key(label):
            stats[label] = []
        stats[label].append((value, tstamp))


def main():
    server = StatsServer(('', 22034,), StatsHandler)
    print '>> Starting server on port 22034'
    print
    server.serve_forever()
    return 0

if __name__ == '__main__':
    sys.exit(main())

