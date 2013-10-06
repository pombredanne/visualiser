#!/usr/bin/env python

import os
import tarfile
import re
import StringIO
from mercurial import hg, ui, cmdutil, scmutil, util
from mercurial.node import nullrev
from metrics import metrics

# original version from fnmatch.py without the '\Z(?ms)'
def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            res = res + '.*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    # return res + '\Z(?ms)'
    return res



# def walk(base, exclude_pattern, start_revision, mode, url):
def walk(base, exclude_pattern, start_revision, mode, archive_base, project):
    """walk all revisions contained in the repository"""

    repo = hg.repository(ui.ui(), base)
    c = repo[None]
    if c.modified() or c.added() or c.removed():
        raise util.Abort(_("uncommitted local changes"))

    pats = ()
    # last_revision = get_last_revision(url)
    # if(start_revision and last_revision == 0):
    last_revision = start_revision
    # else:
    #     last_revision += 1
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
        # context['format'] = 'CSV'
        res = metrics.process(context)
        return metrics.format(res, 'CSV')

    def process_revision(revision):
        # change to revision and create metrics
        print 'Processing revision : %s' % revision
        # change repository to revision
        hg.clean(repo, revision)

        # collect files to process
        exclude = re.compile('|'.join([translate(ep) 
            for ep in exclude_pattern]))
        files = [os.path.relpath(os.path.join(dp, name), base) for
            (dp, dn, fn) in os.walk(base)
            for name in fn 
            if not exclude.match(os.path.relpath(os.path.join(dp, name), base))]
        print 'Number of files to process : %d' % len(files)

        return create_metrics(files)
        #post_metrics(revision_metrics, revision, url)


    def write_archive(archive_name, data):
        """write the metrics to archive."""
        tar = tarfile.open(archive_name, 'w:gz')

        # create a file record
        output = StringIO.StringIO(data)
        info = tar.tarinfo()
        info.name = 'metrics.txt'
        # info.uname = 'pat'
        # info.gname = 'users'
        info.size = output.len

        # add the file to the tar and close it
        tar.addfile(info, output)
        tar.close()


    # from commands.py log:
    matchfn = scmutil.match(repo[None], pats, opts)
    #limit = cmdutil.loglimit(opts)
    #count = 0

    #endrev = None
    #if opts.get('copies') and opts.get('rev'):
    #    endrev = max(cmdutil.revrange(repo, opts.get('rev'))) + 1

    df = False
    if opts["date"]:
        df = util.matchdate(opts["date"])

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

    revisions = []
    rev_last_date = -1
    for ctx in cmdutil.walkchangerevs(repo, matchfn, opts, prep):
        rev_date = util.datestr(ctx.date(), '%Y%m%d')
        if(mode == 'daily' and rev_last_date == rev_date):
            #print '%s Skipped rev %s' % (rev_date, ctx.rev())
            pass
        else:
            result = process_revision(ctx.rev())
            datestamp = util.datestr(ctx.date(), '%y%m%d%H')
            if not os.path.exists(os.path.join(archive_base, datestamp)):
                # create the directories
                os.makedirs(os.path.join(archive_base, datestamp))
            archive_name = os.path.join(archive_base, datestamp, '%s-%s-metrics.tgz' % (project, datestamp))
            write_archive(archive_name, result)
        rev_last_date = rev_date


def main():
    # list 5 last revisions: hg history --limit 5

    src_base = '/home/mark/sandbox/mozilla-central-src'
    mode = 'daily'
    start_revision = 142389
    exclude_pattern = ('.hg/*,testing/*,other-licenses/*,configure.in,.hg*,*test*,*.txt,*.png,*.svg'
        + ',*.gif,*.icc,*.ttf,*.zip,*.egg,*.hxx,*.mk,*.patch,*.rst,*.html,*.css,*.ini,*.conf,*.cfg'
        + ',*.xml,*.json,*LICENSE*,*README*,*PKG-INFO,*Makefile*,*.profile,*.dtd,*.ico,*.xhtml'
        + ',*AUTHORS,*TODO,*.exe,*MANIFEST,*OWNERS,*CHANGES,*PROBLEMS,*DEPS,*.build,*.properties'
        + '*.manifest')
    project = 'firefox'
    archive_base = '/home/mark/devel/aogaeru/demo/testruns'

    walk(src_base, exclude_pattern.split(','), start_revision, mode, archive_base, project)


if __name__ == '__main__':
    main()
