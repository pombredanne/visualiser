#!/usr/bin/env python

import psyco
psyco.full()

import logging
import sys, os, re
try:
    import json
except ImportError, e:
    import simplejson as json

from restish import http, resource, templating, url
from db import DB

from PIL import Image, ImageDraw
import cStringIO

import time
from layout.treemap import layout, render, get_max_value, lookup, lookup_name
from layout.data_structure import color as color

log = logging.getLogger(__name__)


def tb_o2(metrics, keys, depth=""):
    """This function is use to build a tree from a flat data structure.

    Brief structure what happens to the next element from the list:
    i)   same level: add to result
    ii)  lower level: call tb with remaining list
    iii) higher level: return results and remaining list

    Sample result data structure:
    {"name":"","data":{"comments": 1601043,"mccabe": 387533,
    "sloc": 4280147, "ratio_comment_to_code": 0.37},"children":[...]}}    
    """

    len_depth = len(depth)
    # prepare the result data structure    
    result = {'name': depth, 'data': {}, 'children': []}
    for k in keys:
        # add the metrics to the node data
        if k in ['project', 'file', 'revision', 'language', 'ratio_comment_to_code']:
            continue
        result['data'][k] = 0

    while metrics:
        if not metrics[0][keys['file']].startswith(depth):
            # we found a higher level file -> go up one level
            break
        folder, sep, rest = \
            metrics[0][keys['file']][len_depth:].partition('/')
        if sep:
            # found a lower level file -> go down one level
            res = tb_o2(metrics, keys, depth + folder + '/')
            # add the metrics to the result
            for d in result['data']:
                result['data'][d] += res['data'][d]
        else:
            # found file on this level -> add it as child
            res = {'name': metrics[0][keys['file']],
                'data': {}, 'children': []}
            # add the metrics to the result
            for d in result['data']:
                res['data'][d] = metrics[0][keys[d]]
                result['data'][d] += metrics[0][keys[d]]
            # here we have a special case:
            res['data']['language'] = metrics[0][keys['language']]
            res['data']['ratio_comment_to_code'] = \
                metrics[0][keys['ratio_comment_to_code']]
            metrics.pop(0)
        result['children'].append(res)
    # another special case:
    if result['data']['sloc'] == 0:
        result['data']['ratio_comment_to_code'] = 1.0
    else:
        result['data']['ratio_comment_to_code'] = (
            float(result['data']['comments']) /
            float(result['data']['sloc']))
    return result


class Root(resource.Resource):
    @resource.GET()
    def html(self, request):
        return http.ok([('Content-Type', 'text/html')],
            "<p>Hello from backend!</p>")

    @resource.child('{project}/metrics/{revision}')
    def metrics_full(self, request, segments, **kw):
        return Metrics(**kw), segments

    @resource.child('{project}/metrics/{revision}/{key1}/{key2}')
    def metrics_query(self, request, segments, **kw):
        return Metrics(**kw), segments

    @resource.child('{project}/metrics/{revision}/file/{filename}')
    def metrics_file_details(self, request, segments, **kw):
        return Metrics(**kw), segments

    @resource.child('{project}/lastrevision')
    def lists(self, request, segments, **kw):
        return Revisions(**kw), segments

    @resource.child('image')
    def image(self, request, segments, **kw):
        return Images(**kw), segments

    @resource.child('time')
    def time(self, request, segments, **kw):
        return Time(**kw), segments

    @resource.child('treemap/{project}/{revision}')
    def treemap(self, request, segments, **kw):
        session = request.environ['beaker.session']
        return Treemap(session, **kw), segments

    '''
    @resource.child('zoom/{x}/{y}/{f}')
    def zoom(self, request, segments, **kw):
        session = request.environ['beaker.session']
        return Zoom(session, **kw), segments
    '''
    @resource.child('tooltip')
    def tooltip(self, request, segments, **kw):
        session = request.environ['beaker.session']
        return Tooltip(session, **kw), segments


#    @resource.child('lists/{listid}/items/{itemid}')
#    def items(self, request, segments, **kw):
#        return Items(**kw), segments


class Treemap(resource.Resource):

    def __init__(self, session, project='', revision='', dbname=''):
        self.session = session
        self.revision = revision
        self.project = project
        self.db = DB(dbname=dbname)


    @resource.GET()
    def show(self, request):
        """Create the treemap."""
        if not self.project:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))
        if not self.revision:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))
        log.info('Treemap project: %s, revision: %s' % (self.project, self.revision))
        # get the parameters from the url
        crt_url = url.URLAccessor(request).url
        param_dict = dict(crt_url.query_list)
        width = int(param_dict['width'])
        hight = int(param_dict['hight'])
        log.info('width: %d, hight: %d' % (width, hight))
        size_expr = param_dict['size']
        color_expr = param_dict['color']
        log.info('size expr: %s, color expr: %s' % (size_expr, color_expr))
        
        # if possible load data from session
        # read data from the session
        try:
            data = self.session['treemap']
        except KeyError:
            data = None
        if (data and data['project'] == self.project and 
                data['revision'] == self.revision):
            log.info('Retrieved data from cache')
            # retrieve some treemap configs
            zoom = data['zoom']
            try:
                pos_x = int(param_dict['pos_x'])
                pos_y = int(param_dict['pos_y'])
                zoom_factor = int(param_dict['zoom_factor'])
            except KeyError:
                zoom_factor = None
            if zoom_factor and pos_x and pos_y:
                log.info('Zoom %d, %d, factor %d' % (pos_x, pos_y, zoom_factor))
                # client requested zooming
                # calculate zoom target
                if zoom_factor > 0:
                    # Zoom out
                    if zoom.endswith('/'):
                        zoom = zoom[:-1]
                    if zoom.find('/') < abs(zoom_factor):
                        # Zoom to top level
                        zoom = ''
                    else:
                        zoom = '/'.join(zoom.split('/')[:-abs(zoom_factor)])+'/'
                else:
                    # Zoom in
                    if zoom != '':
                        node = lookup_name([data], zoom)
                        path = lookup([node], pos_x, pos_y)['name']
                    else:
                        path = lookup([data], pos_x, pos_y)['name']
                    print 'Path: %s' % path
                    if not(path.startswith(zoom)):
                        raise Booooom
                    path_elements = path.split('/')
                    zoom_length = len(zoom.split('/'))
                    if zoom_length + abs(zoom_factor) >= path_elements:
                        # Full zoom 
                        zoom = path
                    else:
                        zoom = '/'.join(path_elements[:zoom_length + abs(zoom_factor) -1])+'/'
        else:
            # load data from the database
            cols, metrics = self.db.get_metrics_by_revision(self.project, self.revision)
            key_dict = {}
            for i,k in enumerate(cols):
                key_dict[k]=i
            if metrics:
                # create a treemap from the database data
                data = tb_o2(metrics, key_dict)
            else:
                return http.not_found([('Content-type',
                    'application/json')], json.dumps(self.revision))
            zoom = ''
            log.info('Retrieved data from database')

        # TODO: add parameters for size, color, name and treemapid

        img = Image.new('RGBA', (width, hight), (0, 0, 0, 0)) 
        draw = ImageDraw.Draw(img)

        node = lookup_name([data], zoom)

        # helper functions for area and color_value
        def size(node):
            return eval(size_expr, dict(__builtins__=None, True=True, False=False), node['data'])
        def color_value(node):
            return eval(color_expr, dict(__builtins__=None, True=True, False=False), node['data'])

        # inject the max value into the function used for coloring the treemap
        #color.max_value = get_max_value([data], color_value)
        #print 'Color max. value: %d' % color.max_value
        color.color_value = color_value

        # create treemap layout
        layout([node], width, hight, size=size)

        # save some treemap configuration with the data
        data['project'] = self.project
        data['revision'] = self.revision
        data['zoom'] = zoom

        # save data in session
        self.session['treemap'] = data
        self.session.save() # this is necessary!
        
        render(draw, [node], color=color, size=size)
        # save the image to file
        f = cStringIO.StringIO()
        img.save(f, 'png')
        f.seek(0)

        return http.ok([('Content-type', 'image/png')], f.read())


class Tooltip(resource.Resource):
    def __init__(self, session):
        self.session = session
        # conversions should be done here!

    @resource.GET()
    def show(self, request):
        """Produce Tooltip for x/y coordinates."""
        # get the parameters from the url
        crt_url = url.URLAccessor(request).url
        param_dict = dict(crt_url.query_list)
        pos_x = int(param_dict['pos_x'])
        pos_y = int(param_dict['pos_y'])
        log.info('Tooltip x: %d, y: %d' % (pos_x, pos_y))
        
        if not pos_x:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))
        if not pos_y:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))

        # read data from the session
        data = self.session['treemap']

        if data:
            zoom = data['zoom']
            # Sample data['children'][1] = 
            # {'data': {'mccabe': 4, 'ratio_comment_to_code': 5.6799999999999997, 
            # 'language': 'Bash', 'comments': 108, 'sloc': 19}, 'name': 'allmakefiles.sh',
            # 'rectangle': (599, 1, 600, 2), 'children': []}
            #result = data['children'][1]
            if zoom != '':
                node = lookup_name(data['children'], zoom)
                result = lookup([node], pos_x, pos_y)
            else:
                result = lookup(data['children'], pos_x, pos_y)
        else:
            result = {'info': 'Tooltip data not available, your session probably timed out.'}
        #print result

        #result['data']['pos_x'] = pos_x
        #result['data']['pos_y'] = pos_y
        
        if param_dict.has_key('callback'):
            return http.ok([('Content-type', 'application/x-javascript')],
                param_dict['callback'] + '(' + 
                json.dumps(result) + ')')
        else:
            return http.ok([('Content-type', 'application/json')], json.dumps(result))


class Time(resource.Resource):

    @resource.GET()
    def show(self, request):
        crt_url = url.URLAccessor(request).url
        param_dict = dict(crt_url.query_list)
        print 'time done'
        if param_dict.has_key('callback'):
            return http.ok([('Content-type', 'application/x-javascript')],
                param_dict['callback'] + '(' + 
                json.dumps({'ts': str(time.time()) }) + ')')
        else:
            return http.ok([('Content-type', 'application/json')], json.dumps({'ts': str(time.time()) }))
        #return http.ok([('Content-type', 'text/html')], '<p>' + str(time.time()) + '</p>' )
                
    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)


class Images(resource.Resource):

    '''    def __init__(self, listid="", dbname=""):
        self.revision = listid
        log.info(self.revision)
        self.db = DB(dbname=dbname) '''

    @resource.GET()
    def show(self, request):
        input = Image.new('RGBA', (1000, 1000), (0, 0, 0, 0)) 
        draw = ImageDraw.Draw(input)

        colors = ['black', 'white', 'green', 'red', 'blue', 'brown', 'orange']

        for x in xrange(0,100):
            for y in xrange(0,100):
                colorindex = (x+y)%7
                draw.rectangle((x*10,y*10,(x+1)*10,(y+1)*10), fill=colors[colorindex])
                #print 'Colorindex: %i' % colorindex

        # save the image to file
        #input.save('draw_10k.png', 'png')
        f = cStringIO.StringIO()
        input.save(f, 'png')
        f.seek(0)
        print 'image done'
        return http.ok([('Content-type', 'image/png')], f.read())
                
    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)


class Revisions(resource.Resource):

    def __init__(self, listid="", dbname=""):
        self.revision = listid
        log.info(self.revision)
        self.db = DB(dbname=dbname)

    @resource.GET()
    def show(self, request):
        lastrevision = self.db.get_last_revision()
        if lastrevision:
            return http.ok([('Content-type', 'application/json')],
                json.dumps(lastrevision))
        else:
            return http.not_found([('Content-type', 'application/json')], None)
                
    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)


class Metrics(resource.Resource):

    def __init__(self, project='', revision='', dbname=''):
        self.revision = revision
        log.info(self.revision)
        self.project = project
        log.info(self.project)
        self.db = DB(dbname=dbname)

    def tb_o2(self, metrics, keys, depth=""):
        """This function is use to build a tree from a flat data structure.

        Brief structure what happens to the next element from the list:
        i)   same level: add to result
        ii)  lower level: call tb with remaining list
        iii) higher level: return results and remaining list

        Sample result data structure:
        {"name":"","data":{"comments": 1601043,"mccabe": 387533,
        "sloc": 4280147, "ratio_comment_to_code": 0.37},"children":[...]}}    
        """

        len_depth = len(depth)
        # prepare the result data structure    
        result = {'name': depth, 'data': {}, 'children': []}
        for k in keys:
            # add the metrics to the node data
            if k in ['project', 'file', 'revision', 'language', 'ratio_comment_to_code']:
                continue
            result['data'][k] = 0

        while metrics:
            if not metrics[0][keys['file']].startswith(depth):
                # we found a higher level file -> go up one level
                break
            folder, sep, rest = \
                metrics[0][keys['file']][len_depth:].partition('/')
            if sep:
                # found a lower level file -> go down one level
                res = self.tb_o2(metrics, keys, depth + folder + '/')
                # add the metrics to the result
                for d in result['data']:
                    result['data'][d] += res['data'][d]
            else:
                # found file on this level -> add it as child
                res = {'name': metrics[0][keys['file']],
                    'data': {}, 'children': []}
                # add the metrics to the result
                for d in result['data']:
                    res['data'][d] = metrics[0][keys[d]]
                    result['data'][d] += metrics[0][keys[d]]
                # here we have a special case:
                res['data']['language'] = metrics[0][keys['language']]
                res['data']['ratio_comment_to_code'] = \
                    metrics[0][keys['ratio_comment_to_code']]
                metrics.pop(0)
            result['children'].append(res)
        # another special case:
        if result['data']['sloc'] == 0:
            result['data']['ratio_comment_to_code'] = 1.0
        else:
            result['data']['ratio_comment_to_code'] = (
                float(result['data']['comments']) /
                float(result['data']['sloc']))
        return result

    @resource.GET()
    def show(self, request):
        """Query full metrics by revision."""
        crt_url = url.URLAccessor(request).url
        #print crt_url
        #print crt_url.query_list
        param_dict = dict(crt_url.query_list)
        
        if not self.project:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))
        if not self.revision:
            return http.not_found([('Content-type', 'application/json')],
                json.dumps(None))
        else:
            cols, metrics = self.db.get_metrics_by_revision(self.project, self.revision)
            key_dict = {}
            for i,k in enumerate(cols):
                key_dict[k]=i

            if metrics:
                if param_dict.has_key('callback'):
                    return http.ok([('Content-type', 'application/json')],
                        param_dict['callback'] + '(' + 
                        json.dumps({'results': self.tb_o2(metrics, key_dict)}) + ')')
                else:
                    return http.ok([('Content-type', 'application/json')],
                        json.dumps({'results': self.tb_o2(metrics, key_dict)}))
            else:
                return http.not_found([('Content-type',
                    'application/json')], json.dumps(self.revision))


    """
    name, data, children...

    {"name":"","data":{"comments": 1601043,"mccabe": 387533,"sloc": 4280147,"ratio_comment_to_code": 0.37},"children":
    [{"name":"accessible/","data":{"comments": 21221,"mccabe": 4589,"sloc": 51258,"ratio_comment_to_code": 0.41}, "children":
    [{"name":"accessible/accessible-docs.html","data":{"language": "HTML","comments": 0,"mccabe": 0,"sloc": 714,"ratio_comment_to_code": 0}},
    {"name":"accessible/build/","data":{"language": "Makefile","comments": 111,"mccabe": 1,"sloc": 71,"ratio_comment_to_code": 1.56}, "children":
    [{"name":"accessible/build/Makefile.in","data":{"language": "Makefile","comments": 74,"mccabe": 0,"sloc": 31,"ratio_comment_to_code": 2.39}},
    {"name":"accessible/build/nsAccessibilityFactory.cpp","data":{"language": "C++","comments": 37,"mccabe": 1,"sloc": 40,"ratio_comment_to_code": 0.93}}]
    },
    {"name":"accessible/Makefile.in","data":{"language": "Makefile","comments": 72,"mccabe": 0,"sloc": 11,"ratio_comment_to_code": 6.55}},
    {"name":"accessible/public/","data":{"comments": 292,"mccabe": 1,"sloc": 181,"ratio_comment_to_code": 1.61}, "children":
    [{"name":"accessible/public/ia2/","data":{"language": "Modula-2","comments": 78,"mccabe": 1,"sloc": 35,"ratio_comment_to_code": 2.23}, "children":
    ...

           "descendants": {
               "map":
    function(doc) {
      if(doc["file"] !== undefined) {
        var pathelements = doc["file"].split("/");
        var path = ""; // used as root of the tree
        for (var idx = 0; idx < pathelements.length; idx++) {
            next = pathelements[idx];
            if (idx < pathelements.length-1) {
                next += "/";
            }
            emit([doc.revision, path, next], 1);
            path = path + next;
        }
      }
    }"""

               
    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.POST(content_type='json')
    def create_metrics(self, request):
        if self.revision:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        metrics_dict = json.loads(request.body, 'utf-8')
        metrics = metrics_dict.get('metrics')
        if not metrics:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        # split metrics dictionary into keys and values & ascii encoding
        #keys = [s.encode('utf-8') for s in metrics[0].keys()]
        keys = [s.encode('utf-8') for s in metrics[0].keys()]
        # values is a list of metrics
        # caution: no verificaiton that each metrics has the format in keys
        values = [[s.encode('utf-8') if (type(s) == unicode) else s 
            for s in m.values()] for m in metrics]

        self.db.insert_metrics(keys, values)
        crt_url = url.URLAccessor(request).url
        log.info(crt_url)
        new_url = crt_url + str(self.revision)
        return http.Response('201 Created', [ ('Location', new_url) ], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT(content_type='json')
    def modify_list(self, request):
        if not self.revision:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        metrics_dict = json.loads(request.body)
        metrics = listdict.get('metrics')
        if not metics:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        self.db.modify_metrics(self.revision, metrics)
        return http.ok([('Content-type', 'application/json')], json.dumps({self.revision:metrics}))
        
        
        
"""        
class Lists(resource.Resource):

    def __init__(self, listid="", dbname=""):
        self.listid = listid
        log.info(self.listid)
        self.db = DB(dbname=dbname)

    @resource.GET()
    def show(self, request):
        if not self.listid:
            all_lists = self.db.get_all_lists()
            return http.ok([],json.dumps(all_lists))
        else:
            listname = self.db.get_list_by_id(self.listid)
            if listname:
                return http.ok([('Content-type', 'application/json')],json.dumps(listname))
            else:
                return http.not_found([('Content-type', 'application/json')],json.dumps(listname))
                
    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.POST(content_type='json')
    def create_list(self, request):
        if self.listid:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        listdict = json.loads(request.body)
        listname = listdict.get('file')
    if not listname:
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        listid = self.db.insert_list(listname)
        crt_url = url.URLAccessor(request).url
    log.info(crt_url)
    new_url = crt_url + str(listid)
        return http.Response('201 Created', [ ('Location', new_url) ], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT(content_type='json')
    def modify_list(self, request):
        if not self.listid:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        listdict = json.loads(request.body)
        listname = listdict.get('file')
    if not listname:
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        self.db.modify_list(self.listid, listname)
        return http.ok([('Content-type', 'application/json')], json.dumps({self.listid:listname}))



class Items(resource.Resource):

    def __init__(self, listid, itemid):
        self.listid = listid
        self.itemid = itemid
    log.info(listid)
    log.info(itemid)
        self.db = DB()

    @resource.GET()
    def show(self, request):
        if not self.listid:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        if not self.itemid:
            list_items = self.db.get_list_items(self.listid)
            return http.ok([('Content-type', 'application/json')],json.dumps(list_items))
        else:
            item_body = self.db.get_item(self.listid, self.itemid)
        if item_body:
                return http.ok([('Content-type', 'application/json')],json.dumps(item_body))
            else:
                return http.not_found([('Content-type', 'application/json')],json.dumps(item_body))

    @resource.POST()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.POST(content_type='json')
    def create_item(self, request):
        if not self.listid or self.itemid:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        itemdict = json.loads(request.body)
        itemname = itemdict.get('file')
    if not itemname:
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        itemid = self.db.insert_item(self.listid, itemname)
        crt_url = url.URLAccessor(request).url
    log.info(crt_url)
    new_url = crt_url + str(itemid)
        return http.Response('201 Created', [ ('Location', new_url) ], None)

    @resource.PUT()
    def put_default(self, request):
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)

    @resource.PUT(content_type='json')
    def modify_item(self, request):
        if not self.listid or not self.itemid:
            return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
    log.info(request.body)
        itemdict = json.loads(request.body)
        itemname = itemdict.get('file')
    log.info(itemname)
    if not itemname:
        return http.Response('501 Not Implemented', [('Content-type', 'application/json')], None)
        self.db.modify_item(self.listid, self.itemid, itemname)
        return http.ok([('Content-type', 'application/json')], json.dumps({self.itemid:itemname}))
"""
