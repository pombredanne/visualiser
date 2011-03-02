"""
Treemap builder using pylab.

Uses algorithm straight from http://hcil.cs.umd.edu/trs/91-03/91-03.html

James Casbon 29/7/2006
"""

import pylab
from matplotlib.patches import Rectangle
import json
from data_structure import color

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


class Treemap:
    def __init__(self, tree, iter_method, size_method, color_method):
        """create a tree map from tree, using itermethod(node) to walk tree,
        size_method(node) to get object size and color_method(node) to get its 
        color"""

        self.ax = pylab.subplot(111,aspect='equal')
        pylab.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.size_method = size_method
        self.iter_method = iter_method
        self.color_method = color_method
        self.addnode(tree)

    def addnode(self, node, lower=[0,0], upper=[1,1], axis=0):
        axis = axis % 2
        self.draw_rectangle(lower, upper, node)
        width = upper[axis] - lower[axis]
        try:
            for child in self.iter_method(node['children']):
                #upper[axis] = lower[axis] + (width * float(size(child))) / size(node)
                if size(node):
                    upper[axis] = lower[axis] + (width * float(size(child))) / size(node)
                else:
                    upper[axis] = 0
                self.addnode(child, list(lower), list(upper), axis + 1)
                lower[axis] = upper[axis]

        except KeyError:
            pass

    def draw_rectangle(self, lower, upper, node):
        print lower, upper
        r = Rectangle( lower, upper[0]-lower[0], upper[1] - lower[1],
                   edgecolor='k',
                   facecolor= self.color_method(node))
        self.ax.add_patch(r)


if __name__ == '__main__':
    # example using nested lists, iter to walk and random colors

    #size_cache = {}
    #def size(thing):
    #    if isinstance(thing, int):
    #        return thing
    #    if thing in size_cache:
    #        return size_cache[thing]
    #    else:
    #        size_cache[thing] = reduce(int.__add__, [size(x) for x in thing])
    #        return size_cache[thing]
    def size(thing):
        return thing['data']['sloc']
    import random
    def random_color(thing):
        return (random.random(),random.random(),random.random())

    #with open('treemap_data_03.json', 'r') as f:
    #    data = json.load(f) 

    global data
    #tree= ((5,(3,5)), 4, (5,2,(2,3,(3,2,2)),(3,3)), (3,2) )
    #Treemap(tree, iter, size, random_color)
    Treemap(data, iter, size, random_color)
    
    print 'heyho'
    #pylab.show()
    pylab.savefig('draw_mpl_treemap.png')

