#! /usr/bin/env python

import sys
import ConfigParser
#from datastore_helper import initialize_db

def read_config(filename):
    """Read ini file configuration"""
    cp = ConfigParser.ConfigParser()
    cp.read(filename)

    config = {}

    config['base'] = cp.get('repository', 'base')
    config['walker'] = cp.get('repository', 'walker')
    config['mode'] = cp.get('repository', 'mode')
    config['start_revision'] = cp.get('repository', 'start_revision')
    config['exclude_pattern'] = cp.get('repository', 'exclude_pattern').split(',')
    config['url'] = cp.get('visualizer', 'url')

    return config


def usage():
    """Print the visualizer usage help."""
    print "Run visualizer on a repository    -> visualizer.py config_file.ini"
    print "Initialize a repository           -> visualizer.py config_file.ini initialize"
    print "Display this help                 -> visualizer.py help"
    sys.exit(-1)


def walk(config):
    """Invoke the repository walker."""
    walker = __import__(config['walker'], fromlist=['walk'])
    walker.walk(config['base'], config['exclude_pattern'], 
        config['start_revision'], config['mode'], config['url'])


def main():
    """Handle parameters and call the appropriate functions."""
    if len(sys.argv) == 2:
        if sys.argv[1] == 'help':
            usage()
        else:
            config = read_config(sys.argv[1])
            walk(config)
    elif len(sys.argv) == 3 and sys.argv[2] == 'initialize':
        config = read_config(sys.argv[1])
        # Invoke the CouchDb setup from the couchdb_helper.
        initialize_db(config['url'])
    else:
        usage()


if __name__ == '__main__':
    main()
