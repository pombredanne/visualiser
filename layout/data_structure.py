#!/usr/bin/env python

"""
Utility function to access the visualizer data structure. You can use
these as hooks in order to use your own data structure.
"""

    
def area(node):
    """
    Utility function must be replaced if you use a different data structure.
    It is used calculate the area of a node.
    """
    rec = rectangle(node)
    if rec:
        result = (rec[2] - rec[0]) * (rec[3] - rec[1])
    else:
        result = 0
    return result


def children(node):
    """
    Utility function must be replaced if you use a different data structure.
    It is used get the children property of a node.
    """
    try:
        children = node['children']
    except KeyError:
        children = []
    return children


def color(node):
    """
    Provide the color of the rectangle which is representing the node.
    The color is calculated by interpolating a node color property
    value range with a real RGB color range. 
    By specifying min/max values for the property and min/max for 
    color values for the RGB counterparts, the visualization is able
    to interpolate color values and assign a proper color to the node.
    min_value: The minimum value expected for the color value property.
    max_value: The maximum value expected for the color value property.
    min_color_value: A three-element RGB array defining the color to
        be assigned to the node having min_value as value. Default is [255, 0, 50].
    max_color_value: A three-element RGB array defining the color to
        be assigned to the node having max_value as value. Default's [0, 255, 50].
    """
	# function which is used to access the color value of the node
    color_value = mccabe

    def comp(i, x):
        return int(round(((max_color_value[i] - min_color_value[i]) /
            (max_value - min_value)) * (x - min_value) + min_color_value[i]))
    #  return Math.round((((maxcv[i] - mincv[i]) / diff) * (x - minv) + mincv[i])); 
    min_value = 0
    max_value = 250 # use the value from get_max_value
    min_color_value = (0, 255, 50)
    max_color_value = (255, 0, 50)
    x = color_value(node) # access the nodes color property
    col = (comp(0, x), comp(1, x), comp(2, x))
    #print 'Color: %s' % str(col)
    return col
    

def mccabe(node):
    """
    Utility function must be replaced if you use a different data structure.
    It is used get the mccabe property of a node.
    """
    # set or get the rectangle calculated by the layout function
    try:
        attr = node['data']['mccabe']
    except KeyError:
        attr = None
    return attr
    

def name(node):
    """
    Utility function must be replaced if you use a different data structure.
    It is used get the name property of a node.
    """
    # set or get the rectangle calculated by the layout function
    try:
        attr = node['name']
    except KeyError:
        attr = None
    return attr


def transpose_rectangle(rect, transpose=False):
    """
    Utility function to transpose coordinates of a rectangle
    """
    if transpose:
        return [rect[1], rect[0], rect[3], rect[2]]
    else:
        return rect


def rectangle(node, rect=None, transpose=False):
    """
    Utility function must be replaced if you use a different data structure.
    It is used to set or get the rectangle of a node. The rectangle is 
    calculated by the layout function.
    """
    try:
        if rect:
            node['rectangle'] = transpose_rectangle(rect, transpose)
        else:
            rect = node['rectangle']
    except KeyError:
        rect = None
    return rect


def size(node):
    """
    Utility function must be replaced if you use a different data structure.
    It is used get the size property of a node.
    """
    # set or get the rectangle calculated by the layout function
    try:
        attr = node['data']['sloc']
    except KeyError:
        attr = None
    return attr


