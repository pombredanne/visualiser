#!/usr/bin/env python

import unittest
#import filecmp
#import cStringIO
from PIL import Image, ImageDraw
import ImageChops
import json
from layout.treemap import layout, render, lookup, lookup_name
from layout.data_structure import *

def test_treemap_01():
    """Create a treemap based on sample data and compare to file"""

    data = {"name":"","data":{"mccabe": 387533,"sloc": 240000}, "children":[
        {"name":"ch1","data":{"mccabe": 1,"sloc": 60000}, "children":[]},
        {"name":"ch2","data":{"mccabe": 2,"sloc": 60000}, "children":
        [
        ]},
        {"name":"ch3","data":{"mccabe": 3,"sloc": 40000}, "children":
        [
        ]},
        {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
        {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
        {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
        {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
        ]}

    verify_treemap(data, 600, 400, 'tests/images/test_treemap_01.png')


def test_treemap_02():
    """Treemap with children"""

    data = {"name":"","data":{"mccabe": 387533,"sloc": 240000}, "children":[
        {"name":"ch1","data":{"mccabe": 1,"sloc": 60000}, "children":[]},
        {"name":"ch2","data":{"mccabe": 2,"sloc": 60000}, "children":
        [
        {"name":"ch2.1","data":{"mccabe": 2,"sloc": 25000}, "children":[]},
        {"name":"ch2.2","data":{"mccabe": 3,"sloc": 15000}, "children":[]},
        {"name":"ch2.3","data":{"mccabe": 4,"sloc": 15000}, "children":[]},
        {"name":"ch2.4","data":{"mccabe": 5,"sloc":  5000}, "children":[]}
        ]},
        {"name":"ch3","data":{"mccabe": 3,"sloc": 40000}, "children":
        [
        {"name":"ch3.1","data":{"mccabe": 6,"sloc": 15000}, "children":[]},
        {"name":"ch3.2","data":{"mccabe": 7,"sloc": 15000}, "children":[]},
        {"name":"ch3.3","data":{"mccabe": 8,"sloc": 7000}, "children":[]},
        {"name":"ch3.4","data":{"mccabe": 9,"sloc": 3000}, "children":[]}
        ]},
        {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
        {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
        {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
        {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
        ]}

    verify_treemap(data, 600, 400, 'tests/images/test_treemap_02.png')

'''
def test_treemap_03():
    """Big Treemap (Firefox)"""
    #with open('treemap_sample.json', 'r', encoding='utf-8') as f:
    with open('tests/data/treemap_data_03.json', 'r') as f:
        data = json.load(f) 

    verify_treemap(data, 600, 400, 'tests/images/test_treemap_03.png')
'''

def test_treemap_04():
    """Treemap scaled very little"""

    data = {"name":"","data":{"mccabe": 387533,"sloc": 240000}, "children":[
        {"name":"ch1","data":{"mccabe": 1,"sloc": 60000}, "children":[]},
        {"name":"ch2","data":{"mccabe": 2,"sloc": 60000}, "children":
        [
        {"name":"ch2.1","data":{"mccabe": 2,"sloc": 25000}, "children":[]},
        {"name":"ch2.2","data":{"mccabe": 3,"sloc": 15000}, "children":[]},
        {"name":"ch2.3","data":{"mccabe": 4,"sloc": 15000}, "children":[]},
        {"name":"ch2.4","data":{"mccabe": 5,"sloc":  5000}, "children":[]}
        ]},
        {"name":"ch3","data":{"mccabe": 3,"sloc": 40000}, "children":
        [
        {"name":"ch3.1","data":{"mccabe": 6,"sloc": 15000}, "children":[]},
        {"name":"ch3.2","data":{"mccabe": 7,"sloc": 15000}, "children":[]},
        {"name":"ch3.3","data":{"mccabe": 8,"sloc": 7000}, "children":[]},
        {"name":"ch3.4","data":{"mccabe": 9,"sloc": 3000}, "children":[]}
        ]},
        {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
        {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
        {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
        {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
        ]}

    verify_treemap(data, 15, 10, 'tests/images/test_treemap_04.png')


def test_lookup():
    """Test the lookup function of the treemap layout."""

    data = {"name":"","data":{"mccabe": 387533,"sloc": 240000}, "children":[
        {"name":"ch1","data":{"mccabe": 1,"sloc": 60000}, "children":[]},
        {"name":"ch2","data":{"mccabe": 2,"sloc": 60000}, "children":
        [
        {"name":"ch2.1","data":{"mccabe": 2,"sloc": 25000}, "children":[]},
        {"name":"ch2.2","data":{"mccabe": 3,"sloc": 15000}, "children":[]},
        {"name":"ch2.3","data":{"mccabe": 4,"sloc": 15000}, "children":[]},
        {"name":"ch2.4","data":{"mccabe": 5,"sloc":  5000}, "children":[]}
        ]},
        {"name":"ch3","data":{"mccabe": 3,"sloc": 40000}, "children":
        [
        {"name":"ch3.1","data":{"mccabe": 6,"sloc": 15000}, "children":[]},
        {"name":"ch3.2","data":{"mccabe": 7,"sloc": 15000}, "children":[]},
        {"name":"ch3.3","data":{"mccabe": 8,"sloc": 7000}, "children":[]},
        {"name":"ch3.4","data":{"mccabe": 9,"sloc": 3000}, "children":[]}
        ]},
        {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
        {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
        {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
        {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
        ]}

    width = 600
    hight = 400

    img = Image.new('RGBA', (width, hight), (0, 0, 0, 0)) 
    draw = ImageDraw.Draw(img)

    # create layout
    layout(data['children'], width, hight)
    check_layout_consistency(data['children'])        

    assert(lookup(data['children'], 200,  50)['name'] == 'ch2.3')
    assert(lookup(data['children'], 450, 180)['name'] == 'ch3.4')


def test_lookup_name():
    """Test the lookup by name function of the treemap layout."""

    with open('tests/data/treemap_data_03.json', 'r') as f:
        data = json.load(f) 

    width = 600
    hight = 400

    # create layout
    layout(data['children'], width, hight)

    assert(lookup_name(data['children'], 
        'security/nss/tests/chains/ocspd-config/ocspd-certs.sh')['name'] == 
        'security/nss/tests/chains/ocspd-config/ocspd-certs.sh')
    assert(lookup_name(data['children'], 
        'storage/test/unit/test_statement_wrapper_automatically.js')['name'] == 
        'storage/test/unit/test_statement_wrapper_automatically.js')
    assert(lookup_name([data], '')['name'] == '')


def check_layout_consistency(data):
    """Verify that size of the parent is the same as size of the 
    children"""
    
    for node in data:
        if len(children(node)) > 0 and area(node) > 0:
            rec = rectangle(node)
            area_node = area(node)
            area_frame = (rec[2] - rec[0] - 2) * (rec[3] - rec[1] - 2)
            area_children = sum([area(x) for x in children(node)])
            print 'Node name: %s' % node['name']
            print 'Area node: %i' % area_node
            print 'Area frame: %i' % area_frame
            print 'Area children: %i' % area_children
            assert(area_children == area_node or area_children == area_frame)
            #and for the children
            check_layout_consistency(children(node))


def verify_treemap(data, width, hight, goldfile):
    """Utility to draw treemaps shared by all treemap tests"""

    img = Image.new('RGBA', (width, hight), (0, 0, 0, 0)) 
    draw = ImageDraw.Draw(img)

    gold = Image.open(goldfile)

    # create layout
    layout(data['children'], width, hight)
    check_layout_consistency(data['children'])        

    render(draw, data['children'])
    assert(ImageChops.difference(gold, img).getbbox() is None)


