import logging
import psycopg2

# ported to PostgreSQL by Mark Fink August/2010

log = logging.getLogger(__name__)

DBHOST = 'localhost'
DBNAME = 'metrics'
DBUSER = 'postgres'
DBPASSWD = 'postgres'

class DB:

    def __init__(self, dbhost="", dbname="", dbuser="", dbpasswd=""):
        if not dbhost:
            dbhost = DBHOST
        if not dbname:
            dbname = DBNAME
        if not dbuser:
            dbuser = DBUSER
        if not dbpasswd:
            dbpasswd = DBPASSWD
        self._conn = psycopg2.connect(
            "dbname=%s user=%s password=%s host=%s" %
            (dbname, dbuser, dbpasswd, dbhost))

    def insert_update(self, sql):
        _cursor = self._conn.cursor()
        _cursor.execute(sql)
        _cursor.close()
        self._conn.commit()

    def update(self, sql):
        self.insert_update(sql)

    def insert(self, sql):
        self.insert_update(sql)

    def select(self, sql):
        _cursor = self._conn.cursor()
        _cursor.execute(sql)
        rows = _cursor.fetchall()
        _cursor.close()
        return rows

    def get_metrics_by_revision(self, project, revision):
        """Get column-names and metrics for a revision."""
        sql1 = "select attname from pg_attribute, pg_class where attrelid = pg_class.oid and relname = 'metrics' and attnum > 0 and not(attisdropped) order by attnum"
        sql2 = ("select * from metrics where project='%s' and revision=%s order by file" % 
            (project, revision))
        colnames = self.select(sql1)
        if not colnames:
            return None, None
        rows = self.select(sql2)
        if not rows:
            return None, None
        return list(zip(*colnames)[0]), rows


    """    
    def get_list_items(self, listid):
        sql = "select name from items where listid=%s" % listid
        rows = self.select(sql)
        list_items = []
        for row in rows:
            list_items.append(row[0])
        return list_items

    def get_item(self, listid, itemid):
        sql = "select name from items where listid=%s and id=%s" % (listid, itemid)
        rows = self.select(sql)
        if not rows:
            return None
        return rows[0][0]
    """

    def get_last_revision(self, project):
        sql = 'select max(revision) from metrics where project=%s' % project
        rows = self.select(sql)
        if not rows:
            return None
        return rows[0][0]

    """
    def list_exists(self, listname):
        sql = "select * from lists where name = '%s'" % listname
        rows = self.select(sql)
        return len(rows)

    def modify_list(self, id, listname):
        sql = "update lists set name='%s' where id=%s" % (listname, id)
        self.update(sql)

    def modify_item(self, listid, itemid, itemname):
        sql = "update items set name='%s' where id=%s and listid=%s" % (itemname, itemid, listid)
        self.update(sql)
    """
    def insert_metrics(self, keys, values):
        """values contains a list of metrics"""
        sql = 'insert into metrics ('
        sql += ','.join(keys) + ') values '
        #    'mccabe, filename, sloc, comments, revision' + ') values '
        #    str(keys)[1:-1] + ') values '
        # 'mccabe', 'filename', 'sloc', 'comments'
        for m in values:
            sql += '(' + str(m)[1:-1] + '),'
        self.insert(sql[:-1]) # remove the ',' from the last value

"""
    def insert_item(self, listid, itemname):
        sql = "insert into items (listid,name) values (%s,'%s')" % (listid, itemname)
        self.insert(sql);
        return id
"""
