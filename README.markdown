graphite-tools
===============

This repository contains a number of handy tools for using
[Graphite](http://graphite.wikidot.com) in a production environment,
particularly with Python applications.



aggregated.py
-------------

This daemon is modeled after Etsy's [statsd](https://github.com/etsy/statsd)
and listens for UDP packets with either **timing** information or **count**
information.

For timing information, `aggregated.py` will tabulate the following metrics to
be sent to the Carbon daemon every minute:

  * `avg` - average for the minute
  * `upper` - highest value seen in the minute
  * `lower` - lowest value seen in the minute
  * `count` - total events with this label seen in the minute


For count information, `aggregated.py` will send the **sum** of all the events
to the Carbon daemon every minute.


One example, using both of these methods in conjunction with one another is
when profiling cache hits/misses. For example:


    result = cache.get('mykey')
    if result:
        graphite.incr('app.method.cache.hit')
        return result

    start = time.time()
    result = slow_uncached_method()
    graphite.timing('app.method.cache.miss', (time.time() - start))


The above example would give you the following metrics in Graphite:

  * app.method.cache.hit
  * app.method.cache.miss.avg
  * app.method.cache.miss.count
  * app.method.cache.miss.upper
  * app.method.cache.miss.lower

Using these five metrics you can get total cache hits/misses and plot an
average cache miss time.



monitors
--------

These system monitors are still in development, but are meant to be run from
something like [Jenkins](http://jenkins-ci.org) on a timer to report
information about machines or services running in the production cluster.

