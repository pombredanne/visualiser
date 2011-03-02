#! /usr/bin/env python

"""Sample script to demonstrate time measurements in Python."""

import sys
import httplib2
import math
import timeit

def calculate_results(measurements):
    """Take a list of measurements and calculate results from it.
    Results:
    (minimum, mean, maximum, std. deviation, median, 90th percentile)
    """
    
    def calculate_std(measurements, mean):
        # calculate the standard deviation
        std = 0
        for i in measurements:
            std = std + (i - mean)**2
        return math.sqrt(std/ float(len(measurements)))
    
    def calculate_percentile(m_sorted, percentile):
        # This function calculates the linear interpolation between
        # the two closest ranks (p(k) <= p <= pk+1).
        if not m_sorted:
            return none
        m_sorted.sort()
        if percentile < 0.0:
            return m_sorted[0]
        elif percentile > 1.0:
            return m_osrted[-1]
        k = (len(m_sorted)-1) * percentile
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return m_sorted[int(f)]
        return m_sorted[int(f)] + (m_sorted[int(c)] - 
            m_sorted[int(f)])*(k-f)
    
    # sort the measurements
    measurements.sort()
    
    # calculate the results
    minimum = measurements[0]
    mean = sum(measurements)/ float(len(measurements))
    maximum = measurements[-1]
    std = calculate_std(measurements, mean)
    median = calculate_percentile(measurements, 0.5)
    p90 = calculate_percentile(measurements, 0.9)

    print 'Number of measurements: %d' % len(measurements)
    
    return minimum, mean, maximum, std, median, p90


def execute_statements():
    """Define the statements for your measurement here!"""
    #l = ['abc'] * 10000
    # for the CouchDB data store:
    query = 'http://localhost:5984/firefox/_design/node/_view/metrics?startkey=[42096,%22%22]&endkey=[42096,{}]&group=true'
    # for PostgreSQL + restish data store:
    #query = 'http://localhost:9999/metrics/42096'

    #h = httplib2.Http(".cache")
    h = httplib2.Http() # no caching please!
    resp, content = h.request(query)
    #print "RESPONSE HEADERS:"
    #for k,v in resp.items():
    #    print "%s: %s" % (k, v)
    #
    #print "\nRESPONSE CONTENT:"
    #print content

def main():
    """Execute the measurement and output the results."""
    
    # Note: for small code snippets the garbage collector should 
    # not be enabled!
    t = timeit.Timer(execute_statements, 'gc.enable()')
    
    # repeat the measurement a thousand times
    measurements = t.repeat(50, 1)
    print measurements
    print calculate_results(measurements)


if __name__ == "__main__":
    main()

