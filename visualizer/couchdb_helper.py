#! /usr/bin/env python

import sys
import re
import json
import httplib


class CouchDbError(Exception):
    """Exception used by CouchDb helper"""
    pass


def split_url(url):
    url_re = '^http\://(?P<host>[0-9a-zA-Z\._]+)\:(?P<port>\d+)' + \
        '(?P<database>.*)$'
    match = re.match(url_re, url)
    if match:
        values = match.groupdict()
        return values['host'], int(values['port']), values['database']
    else:
        raise CouchDbError('Invalid CouchDb url: %s' % url)


def get_last_revision(url):
    """Call CouchDb view for the last revision."""
    # http://localhost:5984
    #    /visualizer/_design/lastrevision/_view/lastrevision?group=true
    # split up url
    host, port, database = split_url(url)
    conn = httplib.HTTPConnection(host, port)
    conn.request('GET', database +
        '/_design/node/_view/lastrevision?group=true',
        headers={"Accept": "text/plain"})
    res = conn.getresponse()
    data = json.loads(res.read())
    conn.close()

    if(not res.status == 200):
        raise CouchDbError('Could not exctract last revision from CouchDb.')
    else:
        if(len(data['rows'])):
            last_revision = data['rows'][0]['value']
            return last_revision
        else:
            # database contains no last revision
            return 0


def remove_db(url):
    """Remove the visualizter CouchDb instance from the server."""
    # curl -X DELETE http://127.0.0.1:5984/visualizer
    host, port, database = split_url(url)
    conn = httplib.HTTPConnection(host, port)
    conn.request('DELETE', database, headers={"Accept": "text/plain"})
    res = conn.getresponse()
    conn.close()
    #print res.status, res.reason
    if(not res.status in [200, 404]): # OK, Object Not Found
        raise CouchDbError('Could not remove the visualizter database ' +
            'from the CouchDb server.')


def create_db(url):
    """Create a new visualizter database instance on the CouchDb server."""
    host, port, database = split_url(url)
    conn = httplib.HTTPConnection(host, port)
    conn.request('PUT', database, headers={"Accept": "text/plain"})
    res = conn.getresponse()
    conn.close()
    #print res.status, res.reason

    if(not res.status == 201): # Created
        raise CouchDbError('Could not create the visualizter database ' +
            'on the CouchDb server.')


def load_design(url):
    """Load design into freshly created visualizer database."""
    # curl -v -d @_design_node.json -X PUT
    #    http://127.0.0.1:5984/visualizer/_design/node
    # load node design
    host, port, database = split_url(url)
    conn = httplib.HTTPConnection(host, port)
    fin = open('couchdb/_design_node.json', 'r')
    body = json.dumps(eval(''.join(fin.readlines())))
    fin.close()
    conn.request('PUT', database + '/_design/node', body=body,
        headers={"Accept": "text/plain"})
    res = conn.getresponse()
    #print res.status, res.reason
    if(not res.status == 201): # Created
        raise CouchDbError(
            'Error while uploading design to visualizer database.')
    conn.close()
'''
    # load lastrevision design
    conn = httplib.HTTPConnection(host, port)
    fin = open('couchdb/_design_lastrevision.json', 'r')
    body = json.dumps(eval(''.join(fin.readlines())))
    fin.close()
    conn.request('PUT', database + '/_design/lastrevision', body=body,
        headers={"Accept": "text/plain"})
    res = conn.getresponse()
    #print res.status, res.reason
    if(not res.status == 201): # Created
        raise CouchDbError(
            'Error while uploading design to visualizer database.')
    conn.close()
'''

def post_metrics(metrics, revision, url):
    """
    Post metrics for one revision snapshot to CouchDb.

    metrics format:
    {'filename1': {'sloc': 10, 'mccabe': 11, 'ratio_comment_to_code': 12},
     'filename2': {'sloc': 20, 'mccabe': 21, 'ratio_comment_to_code': 22}}

    target format:
    {"docs": [{"sloc": 30, "ratio_comment_to_code": 1.23, "mccabe": 7,
     "file": "accessible/build/  nsAccessibilityFactory.cpp", "revision":
      26704}, {"sloc": 15, "ratio_comment_to_code": 3.27, "mccabe": 4,
     "file": "accessible/src/atk/nsAccessNodeWrap.cpp", "revision": 26704},

    """
    # dictionary comprehension will be available from <python3 onwards
    data = {'docs': [dict(zip(['file', 'revision']+metrics[m].keys(),
        [m, revision]+metrics[m].values())) for m in metrics]}
    #dict(zip(['a', 'b']+m1.keys(), [1, 2]+m1.values()))
    #curl -v -d @data_26704.json -X POST
    #    http://127.0.0.1:5984/visualizer/_bulk_docs
    # convert metrics into body part of the request
    body = json.dumps(data)

    host, port, database = split_url(url)
    conn = httplib.HTTPConnection(host, port)
    conn.request('POST', database + '/_bulk_docs', body=body,
        headers={"Accept": "text/plain"})
    res = conn.getresponse()
    #print res.status, res.reason
    if(not res.status in [201]): # Created
        raise CouchDbError('Error while uploading revision ' +
            str(revision) + ' metrics to visualizer database.')
    conn.close()


def initialize_db(url):
    """Setup empty visualizer database on the CouchDb server instance."""
    remove_db(url)
    create_db(url)
    load_design(url)


def main():
    """This is useful for some testing/debugging together with CouchDb."""
    try:
        metrics = {'filename1': {'sloc': 10, 'mccabe': 11,
                'ratio_comment_to_code': 12},
            'filename2': {'sloc': 20, 'mccabe': 21,
                'ratio_comment_to_code': 22}}

        #print get_last_revision('http://localhost:5984/visualizer')
        initialize_db('http://localhost:5984/visualizer2')
        #post_metrics(metrics, 123456, 'http://localhost:5984/visualizer')
        return 0
    except Exception, err:
        sys.stderr.write('ERROR: %s\n' % str(err))
        raise
        return 1

if(__name__ == '__main__'):
    sys.exit(main())
