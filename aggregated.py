#!/usr/bin/env python

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

