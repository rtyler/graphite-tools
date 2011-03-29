#!/usr/bin/env python

import socket
import time

AGGREGATED_HOST = '127.0.0.1'
AGGREGATED_PORT = 22034

def aggregator_host():
    return (AGGREGATED_HOST, AGGREGATED_PORT)

def record_multi(dataset):
    """
        Expecting an iterable of (label, value) tuples
    """
    now = time.time()
    lines = ('%s %s %s' % (l, v, now) for l, v in dataset)
    message = '\n'.join(lines) + '\n'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, aggregator_host())

def record(label, value):
    return record_multi(((label, value,),))

def incr(label):
    return record_multi(((label, 1,),))

def timing(label, delta):
    return record(label, '%f|s' % delta)


