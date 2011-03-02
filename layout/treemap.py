#!/usr/bin/env python

#import psyco
#psyco.full()
import copy
from operator import add
from functools import partial
from math import sqrt

from PIL import Image, ImageDraw
from timeit_utils import calculate_results
import timeit
import json
from data_structure import *


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
    ]}
    ,
    {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
    {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
    {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
    {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
    ]}


def layout(indata, width, height, offset_x=0, offset_y=0, scaling=None, 
        children=children, rectangle=rectangle, size=size):
    """
    The ordered treemap preserves the given ordering of the (sorted) data.
    So the user experiences a smooth update when moving from one view
    to the next.

    This function computes the layout of the treemap and stores the information
    as "rectangle" property (use the rectangle(node) access method from 
    data_structure for access).
    
    The layout follows the "pivot-by-middle" algorithm which has
    at worst a n*log(n) performance characteristic.
    """
    def aspect_ratio(a, b):
        # helper
        if a == 0.0 or b == 0.0:
            return 0.0
        elif a < b:
            return float(a)/float(b)
        else:
            return float(b)/float(a)
            
    def p_better(l2, l3, height):
        # helper to determine l2 with an optimum aspect ratio of P
        if len(l3) == 0:
            return False
        sum_l2 = sum(int(round(size(x)*scaling)) for x in indata)
        pw  = sum_l2/float(height)
        if pw == 0:
            return False
        pw1 = (sum_l2 + int(round(size(l3[0])*scaling)))/float(height)
        ar  = aspect_ratio(int(round(size(l2[0])*scaling))/pw, pw)
        ar1 = aspect_ratio(int(round(size(l2[0])*scaling))/pw1, pw1)
        return ar1 > ar
            
    def average(l):
        # helper to compute the average of the list elements
        return reduce(add, l, 0.0)/float(len(l))
            
    l = len(indata)
    
    sum_data = sum([float(size(x)) for x in indata])

    if width == 0 or height == 0 or l == 0 or sum_data == 0:
        # rectangles with size 0 are not visualized!
        # this happens for really small rectangles float => int conversion
        # of the rectangle coordinates
        return

    if height > width:
        tmp = height
        height = width
        width = tmp
        tmp = offset_x
        offset_x = offset_y
        offset_y = tmp
        transpose = True
    else:
        transpose = False

    # scaling for size
    if scaling == None:
        scaling = float(width * height) / sum_data

    # stopping conditions for l <= 4
    if l == 1:
        # for one node no calculation necessary
        rectangle(indata[0], (offset_x, offset_y, offset_x+width,
            offset_y+height), transpose)            
    elif l == 2:
        # snake
        sw0 = int(round(size(indata[0])*scaling/float(height)))
        sw1 = width - sw0

        rectangle(indata[0], (offset_x, offset_y, offset_x+sw0,
            offset_y+height), transpose)            
        rectangle(indata[1], (offset_x+sw0, offset_y,
            offset_x+sw0+sw1, offset_y+height), transpose)
    elif l <= 4:
        # If the number of items is <= 4, lay them out in either
        # a pivot, quad, or snake layout. Use whatever gives the best 
        # aspect ratio.
        sw = [int(round(size(x)*scaling/float(height))) for x in indata]
        sw[-1] = width - sum(sw[:-1]) # correct rounding error for last element
        snake = average(map(partial(aspect_ratio, height), [x for x in sw]))
        # pivot
        pivot = [size(x)*scaling for x in indata]
        ph0 = height
        pw0 = int(round(pivot[0]/float(height)))
        pivot[0] = aspect_ratio(height, pw0)
        pw1 = width - pw0
        if pw1 == 0:
            # to small to be displayed
            pivot[1] = 0
            ph1 = 0
        else:
            ph1 = int(round(pivot[1]/pw1))
            pivot[1] = aspect_ratio(ph1, pw1)
        ph2 = height - ph1
        if ph2 == 0:
            # to small to be displayed
            pivot[2] = 0
            pw2 = 0
        else:
            pw2 = int(round(pivot[2]/ph2))
            pivot[2] = aspect_ratio(ph2, pw2)
        # quad
        quad = [size(x)*scaling for x in indata]
        qw0 = qw1 = int(round((quad[0]+quad[1])/float(height)))
        if qw0 == 0:
            # to small to be displayed
            quad[0] = 0
            quad[1] = 0
        else:
            qh0 = int(round(quad[0]/qw0))
            qh1 = height - qh0
            quad[0] = aspect_ratio(qh0, qw0)
            quad[1] = aspect_ratio(qh1, qw1)
        qw2 = width - qw0
        if qw2 == 0:
            # to small to be displayed
            quad[2] = 0
            qh2 = 0
        else:
            qh2 = int(round(quad[2]/qw2))
            quad[2] = aspect_ratio(qh2, qw2)
        if l == 4:
            # pivot
            ph3 = ph2
            pw3 = pw1 - pw2
            pivot[3] = aspect_ratio(ph3, pw3)
            # quad
            qw3 = qw2
            qh3 = height - qh2
            quad[3] = aspect_ratio(qh3, qw3)
        pivot = average(pivot)
        quad = average(quad)
        
        #print 'Snake: %s' % snake
        #print 'Pivot: %s' % pivot
        #print 'Quad: %s' % quad

        # use what results in the best aspect ratio
        if pivot >= snake and pivot >= quad:
            # pivot
            rectangle(indata[0], (offset_x, offset_y, offset_x+pw0, offset_y+ph0), transpose)
            rectangle(indata[1], (offset_x+pw0, offset_y, 
                offset_x+pw0+pw1, offset_y+ph1), transpose)
            rectangle(indata[2], (offset_x+pw0, offset_y+ph1, 
                offset_x+pw0+pw2, offset_y+ph1+ph2), transpose)
            if l == 4:
                rectangle(indata[3], (offset_x+pw0+pw2, offset_y+ph1,
                    offset_x+pw0+pw2+pw3, offset_y+ph1+ph3), transpose)
        elif snake >= quad:
            # snake
            rectangle(indata[0], (offset_x, offset_y, offset_x+sw[0],
                offset_y+height), transpose)            
            rectangle(indata[1], (offset_x+sw[0], offset_y,
                offset_x+sw[0]+sw[1], offset_y+height), transpose)
            rectangle(indata[2], (offset_x+sw[0]+sw[1], offset_y, 
                offset_x+sw[0]+sw[1]+sw[2], offset_y+height), transpose)
            if l == 4:
                rectangle(indata[3], (offset_x+sw[0]+sw[1]+sw[2], offset_y, 
                    offset_x+sw[0]+sw[1]+sw[2]+sw[3], offset_y+height), transpose)
            pass
        else:
            # quad
            rectangle(indata[0], (offset_x, offset_y, offset_x+qw0, offset_y+qh0), transpose)
            rectangle(indata[1], (offset_x, offset_y+qh0, 
                offset_x+qw1, offset_y+height), transpose)
            rectangle(indata[2], (offset_x+qw0, offset_y, 
                offset_x+qw0+qw2, offset_y+qh2), transpose)
            if l == 4:
                rectangle(indata[3], (offset_x+qw0, offset_y+qh2,
                    offset_x+qw0+qw3, offset_y+height), transpose)

    else:
        # l >= 5
        # this is the "recursive" part of the algorithm
        
        # Divide the nodes in the indata, other than P,
        # into three lists, L1, L2, and L3, such
        # that L1 consist of items whose
        # index is less than P and L2 have
        # items having index less than those
        # in L3, and the aspect ratio of RP is as
        # close to 1 as possible.
        
        l1 = indata[:l/2]
        l2 = [indata[l/2]] # note: Pivot P is l2[0]
        l3 = indata[l/2+1:]
        
        # determin optimum aspect_ratio for Pivot P
        while len(l3) and p_better(l2, l3, height):
            l2.append(l3.pop(0))

        # calculate width of l1, l2, and l3
        w1 = sum(int(round(size(x)*scaling/float(height))) for x in l1)
        if len(l3) > 0:
            w2 = sum(int(round(size(x)*scaling/float(height))) for x in l2)
            w3 = width - w1 - w2
        else:
            w2 = width - w1
            w3 = 0

        # call the layout function for l1, l2, and l3
        layout(l1, *transpose_rectangle([w1, height, offset_x, offset_y], transpose) )
        layout(l2, *transpose_rectangle([w2, height, offset_x+w1, offset_y], transpose) )
        if len(l3):
            layout(l3, *transpose_rectangle([w3, height, offset_x+w1+w2, offset_y], transpose) )
        
    # compute the layout for the children
    if l <= 4:
        for node in indata:
            # compute layout for the children if any
            c = children(node)
            if c:
                r = rectangle(node)
                layout(children(node), r[2]-r[0], r[3]-r[1], r[0], r[1])


'''
def count_nodes(data, children=children):
    """Count the nodes in a data structure including children"""
    result = len(data)
    for node in data:
        result += count_nodes(children(node))
    return result
'''

def get_max_value(data, property, children=children):
    """Look up the maximum value for a given property"""
    result = 0
    for node in data:
        if children(node):
            result = max(result, get_max_value(children(node), property))
        else:
            result = max(result, property(node))
    return result            


def render(draw, data, children=children, color=color, rectangle=rectangle,
        size=size):
    """
    This function renders the rectangles that have been calculated by 
    the layout function.
    """
    for node in data:
        if size(data[0]) == 0:
            # rectangles with size 0 are not rendered!
            continue
        # print 'Name: %s, size: %f' % (data[0]['name'], float(size(data[0])))

        #if len(children(node)) > 0:
        #    fill = 'grey'
        #else:
        #    fill = color(node)

        if rectangle(node):
            #draw.rectangle(rectangle(node), fill=fill)
            draw.rectangle(rectangle(node), fill=color(node))

            if children(node):
                render(draw, children(node), color=color)


def lookup(data, x_position, y_position, children=children, name=name, 
        rectangle=rectangle):
    """
    This function looks up a node for a given position. 
    """
    for node in data:
        r = rectangle(node)
        if r and (r[0] <= x_position <= r[2]) and (r[1] <= y_position <= r[3]):
            found = None
            if children(node):
                found = lookup(children(node), x_position, y_position)
            if found:
                return found
            else:
                # two cases: no children or frame
                return node
    return None


def lookup_name(data, in_name, children=children, name=name):
    """
    This function looks up a node for a given name. 
    """
    for node in data:
        if in_name == name(node):
            return node
        elif in_name.startswith(name(node)):
            return lookup_name(children(node), in_name)
    return None

 
def draw_treemap():
    width = 600
    height = 400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0)) 
    #rectangle(input, (0, 0, 39, 39), "lightblue", "blue", 5)
    draw = ImageDraw.Draw(img)

    #global data
    with open('treemap_data_03.json', 'r') as f:
        data = json.load(f) 


    # TODO: setting the max_value in this way does not work!!!!!!!!!!!
    #color.max_value = get_max_value(data['children'], mccabe)
    #print 'Max mccabe: %i' % color.max_value
    #color.max_value = 10
    #print 'Max mccabe: %i' % color.max_value
    
    layout(data['children'], width, height)
    render(draw, data['children'], color=color)
    # save the image to file
    img.save('draw_treemap_pivot.png', 'png')
    #print 'Lookup: %s' % lookup(data['children'], 599,1)


def main():
    """Execute the measurement and output the results."""

    # make sure data is sorted
    # sort nodes by name if not sorted
    #indata = sorted(indata, key=name, reverse=False)

    
    # Note: for small code snippets the garbage collector should 
    # not be enabled!
    t = timeit.Timer(draw_treemap, 'gc.enable()')
    
    # repeat the measurement a thousand times
    measurements = t.repeat(1, 1)
    print measurements
    print calculate_results(measurements)


if __name__ == "__main__":
    main()

