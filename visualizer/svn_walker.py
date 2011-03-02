#!/usr/bin/env python

#from mercurial import hg, ui, commands, cmdutil, util
import pysvn
import time

def main():
    """walk over all revisions contained in the repository"""

    client = pysvn.Client()

    revs = client.log('./python_trunk')

    for r in revs:
        print time.strftime('%Y%m%d', time.gmtime(r['date'])), r['revision'].number

#    repo = hg.repository(ui.ui(), './mozilla-central')

# #   get = util.cachefunc(lambda r: repo[r].changeset())
#    changeiter, matchfn = cmdutil.walkchangerevs(ui, repo, (), get, 
#        {'rev': '', 'date': '', 'user': ''})
#    rev = -1
#    daily_build = True; # if true process only the last revision of the day
#    revisions = []
#    rev_last_date = -1
#    for st, rev, fns in changeiter:
#        if(rev == False):
#            continue
#        rev_date = util.datestr(get(rev)[2], '%Y%m%d')
#        if(daily_build and rev_last_date == rev_date):
#            #print '%s Skipped rev %s' % (rev_date, rev)
#            pass
#        else:
#            revisions.append(rev)
#            # print '%s Added rev %s' % (rev_date, rev)
#        rev_last_date = rev_date       
           
#    for r in revisions:
#        print r
    

if __name__ == '__main__':
    main()
