#!/usr/bin/env python

import os
import fnmatch
import re
from mercurial import hg, ui, cmdutil, util
from mercurial.node import nullrev
from metrics import metrics
from datastore_helper import get_last_revision, post_metrics
import pygments.util

def walk(base, exclude_pattern, start_revision, mode, url):
    """walk all revisions contained in the repository"""

    repo = hg.repository(ui.ui(), base)
    c = repo[None]
    if c.modified() or c.added() or c.removed():
        raise util.Abort(_("uncommitted local changes"))

    pats = ()
    last_revision = get_last_revision(url)
    if(start_revision and last_revision == 0):
        last_revision = start_revision
    else:
        last_revision += 1
    opts = {'rev': [str(last_revision) + ':'], 'date': '', 'user': ''}

    def create_metrics(in_file_names):
        # create the metrics from the current revision
        context = {}
        context['base'] = base
        context['in_file_names'] = in_file_names
        context['include_metrics'] = [
            ('sloc', 'SLOCMetric'), ('mccabe', 'McCabeMetric')]
        context['quiet'] = True
        context['verbose'] = False
        res = metrics.process(context)
        return res

    def process_revision(revision):
        # change to revision and create metrics
        print 'Processing revision : %s' % revision
        # change repository to revision
        hg.clean(repo, revision)

        # collect files to process
        epre = re.compile('|'.join([fnmatch.translate(ep) 
            for ep in exclude_pattern]))
        files = [os.path.relpath(os.path.join(dp, name), base) for
            (dp, dn, fn) in os.walk(base)
            for name in fn 
            if not epre.match(os.path.relpath(os.path.join(dp, name), base))]
        #files = [os.path.join(os.path.relpath(dp, base), name) for
        #    (dp, dn, fn) in os.walk(base) for name in fn]
        #print 're pattern %s' % '|'.join([fnmatch.translate(ep) 
        #    for ep in exclude_pattern])
        print 'Number of files to process : %d' % len(files)
        #print files
        #in_file_names = [files[500], files[-1]]
        in_file_names = files

        revision_metrics = create_metrics(in_file_names)
        post_metrics(revision_metrics, revision, url)

    # from commands.py log:
    matchfn = cmdutil.match(repo, pats, opts)
    #limit = cmdutil.loglimit(opts)
    #count = 0

    #endrev = None
    #if opts.get('copies') and opts.get('rev'):
    #    endrev = max(cmdutil.revrange(repo, opts.get('rev'))) + 1

    df = False
    if opts["date"]:
        df = util.matchdate(opts["date"])

    #displayer = cmdutil.show_changeset(ui, repo, opts, True, matchfn)
    def prep(ctx, fns):
        rev = ctx.rev()
        parents = [p for p in repo.changelog.parentrevs(rev)
                   if p != nullrev]
        if opts.get('no_merges') and len(parents) == 2:
            return
        if opts.get('only_merges') and len(parents) != 2:
            return
        if opts.get('only_branch') and ctx.branch() not in opts['only_branch']:
            return
        if df and not df(ctx.date()[0]):
            return
        if opts['user'] and not [k for k in opts['user'] if k in ctx.user()]:
            return
        if opts.get('keyword'):
            for k in [kw.lower() for kw in opts['keyword']]:
                if (k in ctx.user().lower() or
                    k in ctx.description().lower() or
                    k in " ".join(ctx.files()).lower()):
                    break
            else:
                return

        #copies = None
        #if opts.get('copies') and rev:
        #    copies = []
        #    getrenamed = templatekw.getrenamedfn(repo, endrev=endrev)
        #    for fn in ctx.files():
        #        rename = getrenamed(fn, rev)
        #        if rename:
        #            copies.append((fn, rename[0]))

    revisions = []
    rev_last_date = -1
    for ctx in cmdutil.walkchangerevs(repo, matchfn, opts, prep):
        rev_date = util.datestr(ctx.date(), '%Y%m%d')
        if(mode == 'daily' and rev_last_date == rev_date):
            #print '%s Skipped rev %s' % (rev_date, ctx.rev())
            pass
        else:
            process_revision(ctx.rev())
            #print '%s Added   rev %s' % (rev_date, ctx.rev())
        rev_last_date = rev_date
