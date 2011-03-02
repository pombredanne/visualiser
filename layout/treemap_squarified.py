#!/usr/bin/env python

#import psyco
#psyco.full()

from PIL import Image, ImageDraw
from timeit_utils import calculate_results
import timeit
import json
import copy
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
    ]},
    {"name":"ch4","data":{"mccabe": 4,"sloc": 30000}, "children":[]},
    {"name":"ch5","data":{"mccabe": 5,"sloc": 20000}, "children":[]},
    {"name":"ch6","data":{"mccabe": 6,"sloc": 20000}, "children":[]},
    {"name":"ch7","data":{"mccabe": 7,"sloc": 10000}, "children":[]}
    ]}


def layout(indata, width, hight, scaling=None, offset_x=0, offset_y=0,
        children=children, rectangle=rectangle, size=size):
    """
    This function lays out the rectangles in horizontal and vertical rows.
    When a rectangle is processed, a decission is made between two alternatives.
    Either the rectangle is added to the current row, or the current row is
    finished and a new row is started in the remaining half of the rectangle.
    This decision depends only on wheather adding a rectangle to the row will
    improve the layout of the current row or not.
    """
    if width == 0 or hight == 0:
        # rectangles with size 0 are not visualized!
        # this happens for really small rectangles float => int conversion
        # of the rectangle coordinates
        return
    
    # sort nodes by size if not sorted
    indata = sorted(indata, key=size, reverse=True)
    
    data = copy.copy(indata) # shallow copy so I can pop() from the list
    
    #print 'Nodes: %s' % ' '.join([x['name'] for x in data])
    #print 'Width: %i, hight: %i' % (width, hight)
    aspect_ratio = None
    row = [] # the rectangles that go into the first half
    area = 0.0
    # in the beginning area size is 240 x 100
    # if area width > hight : split horizontaly
    if width >= hight:
        # split in left and right
        # print 'horiz'
        orientation = 'horiz'
        side_length = hight
    else:
        # split in top and bottom
        # print 'vert'
        orientation = 'vert'
        side_length = width
    #print 'side length: %f' % side_length

    # the scaling is used so the treemap fits exactly into the given image size
    # note scaling is used to scale areas not sides!
    if scaling == None:
        scaling = (float(width * hight) / 
            sum([float(size(x)) for x in data]))
    elif float(width * hight) * scaling < 8000:
        # scaling is to be finetuned for the last elements
        scaling = (float(width * hight) / 
            sum([float(size(x)) for x in data]))
    #print 'Scaling: %f' % scaling
    
    while(1):
        if data:
            if size(data[0]) == 0:
                # rectangles with size 0 are not visualized!
                data.pop(0)
                continue
            #print 'Name: %s, size: %f' % (data[0]['name'], float(size(data[0])))
            area += float(size(data[0])) * scaling
            new_aspect_ratio = (area ** 2 /
                (float(side_length ** 2) * float(size(data[0])) * scaling))
            if new_aspect_ratio < 1.0:
                new_aspect_ratio = 1.0 / new_aspect_ratio
            #print 'aspect ratio for %s: %f' % (data[0]['name'], new_aspect_ratio)
        if data and (aspect_ratio >= new_aspect_ratio or aspect_ratio == None):
            # add the rectangle to the row
            row.append(data.pop(0))
            aspect_ratio = new_aspect_ratio
        else:
            # when only two nodes remain: vert or horiz split?
            # (note: this should be covered by the std. case)

            if len(row) == 1 and len(data) == 2:
                if size(data[1]) == 0:
                    # rectangles with size 0 are not visualized!
                    data.pop(1)
                    continue
                # in case row only has one element: test third way to split                 
                # look only at the last two
                split_aspect_ratio = ((float(size(data[0]) + 
                    float(size(data[1]))) * scaling) ** 2 /
                    (side_length ** 2 * size(data[1]) * scaling))
                if split_aspect_ratio < 1.0:
                    split_aspect_ratio = 1.0 / split_aspect_ratio
                
                # only the last element is relevant
                nosplit_aspect_ratio = (side_length ** 2 /
                    (float(size(data[1])) * scaling))
                if nosplit_aspect_ratio < 1.0:
                    nosplit_aspect_ratio = 1.0 / nosplit_aspect_ratio
                    
                #print 'split ar: %f' % split_aspect_ratio
                #print 'nosplit ar: %f' % nosplit_aspect_ratio
                if nosplit_aspect_ratio <= split_aspect_ratio:
                    # split does not improve the aspect ratio so we finish here
                    # if we do not split we have to change the orientation of the row
                    if width >= hight:
                        orientation = 'vert'
                        side_length = width
                    else:
                        # do not split!
                        orientation = 'horiz'
                        side_length = hight
                    
                    row.append(data.pop(0))
                    row.append(data.pop(0))
            
            # the other side (used for drawing and to determine size of the remaining half
            other_side_length = int(round(sum([float(size(x)) for x in row]) * 
                scaling / side_length))
            #print 'other side length: %i' % other_side_length
            if other_side_length == 0:
                # rectangles with size 0 are not visualized!
                # this happens for really small rectangles because of
                # the float => int conversion of the rectangle coordinates
                break

            # draw the row
            #print 'finish row'
            row_offset = 0
            for i, node in enumerate(row):
                # print node['name']
                node_hight = int(round(float(size(node)) *
                    scaling / other_side_length))
                if (row_offset + node_hight) > side_length:
                    #print 'Node_hight correction for %s' % node['name']
                    node_hight = side_length - row_offset
                # if the node has children draw a grey frame
                if children(node):
                    # the frame is only used for rectangles > 8000
                    if float(size(node)) * scaling >= 8000:
                        frame = 1
                    else:
                        frame = 0
                if orientation == 'horiz':
                    node['rectangle'] = (
                        offset_x,
                        offset_y + hight - row_offset - node_hight,
                        offset_x + other_side_length,
                        offset_y + hight - row_offset)
                    # process the node children
                    if children(node):
                        layout(children(node),
                            other_side_length - 2 * frame, 
                            node_hight - 2 * frame, scaling,
                            offset_x + frame, 
                            offset_y + hight - row_offset - node_hight + frame)
                else:
                    node['rectangle'] = (
                        offset_x + row_offset,
                        offset_y + hight - other_side_length,
                        offset_x + row_offset + node_hight,
                        offset_y + hight)
                    # process the node children
                    if children(node):
                        layout(children(node),
                            node_hight - 2 * frame, 
                            other_side_length - 2 * frame, scaling,
                            offset_x + row_offset + frame, 
                            offset_y + hight - other_side_length + frame)
                row_offset += node_hight
            
            # process the remaining data
            if data:
                if orientation == 'horiz':
                    layout(data,
                        width - other_side_length, hight, scaling,
                        offset_x + other_side_length, offset_y)
                else:
                    layout(data,
                        width, hight - other_side_length, scaling,
                        offset_x, offset_y)
            break


def count_nodes(data, children=children):
    """Count the nodes in a data structure including children"""
    result = len(data)
    for node in data:
        result += count_nodes(children(node))
    return result


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

        if len(children(node)) > 0:
            fill = 'grey'
        else:
            fill = color(node)

        if rectangle(node):
            draw.rectangle(rectangle(node), fill=fill)

            if children(node):
                render(draw, children(node))


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
    hight = 400
    img = Image.new('RGBA', (width, hight), (0, 0, 0, 0)) 
    #rectangle(input, (0, 0, 39, 39), "lightblue", "blue", 5)
    draw = ImageDraw.Draw(img)

    with open('treemap_data_03.json', 'r') as f:
        data = json.load(f) 

    # TODO: this does not work
    #color.max_value = get_max_value(data['children'], mccabe)
    #print 'Max mccabe: %i' % color.max_value
    
    layout(data['children'], width, hight)
    render(draw, data['children'], color=color)
    # save the image to file
    img.save('draw_treemap_squarified.png', 'png')
    #print 'Lookup: %s' % lookup(data['children'], 599,1)


def main():
    """Execute the measurement and output the results."""
    
    # Note: for small code snippets the garbage collector should 
    # not be enabled!
    t = timeit.Timer(draw_treemap, 'gc.enable()')
    
    # repeat the measurement a thousand times
    measurements = t.repeat(1, 1)
    print measurements
    print calculate_results(measurements)


if __name__ == "__main__":
    main()

