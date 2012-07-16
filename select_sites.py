'''
http://pymolwiki.org/index.php/select_sites

(c) 2012 Thomas Holder

License: BSD-2-Clause
'''

import os
from pymol import cmd, CmdException

def select_sites(selection='all', filename=None, prefix=None, nice=1, quiet=0):
    '''
DESCRIPTION

    Make named selections from SITE records.

ARGUMENTS

    name = string: molecular object {default: all}

    filename = string: PDB file name with SITE records {default: look in
    current directory and fetch_path for <name>.pdb}

    prefix = string: prefix for named selections {default: site_}

    nice = 0 or 1: make colored sticks representation for sites {default :1}
    '''
    nice, quiet = int(nice), int(quiet)

    names = cmd.get_names('public_objects', 1, '(' + selection + ')')
    selenames = set()

    for name in names:
        pfx = prefix or name + '_'
        fname = filename

        if fname is None:
            for fname in ['%s.pdb' % (name),
                    '%s/%s.pdb' % (cmd.get('fetch_path'), name)]:
                if os.path.exists(fname):
                    break
            else:
                print ' Error: please provide filename'
                raise CmdException
            if not quiet:
                print 'loading from %s' % (fname)

        for line in open(fname):
            if line.startswith('SITE '):
                siteID = line[11:14].strip()
                selename = pfx + siteID
                selenames.add(selename)
                for i in range(4):
                    res = line[18+11*i:29+11*i]
                    if res.strip():
                        chain = res[4]
                        resi = res[5:].strip()
                        selestr = '%s and chain %s and resi %s' % (name, chain, resi)
                        cmd.select(selename, selestr, 0, 1, 1)
            elif line.startswith('LINK '):
                s1 = '%s/%s/%s' % (line[21], line[22:27].strip(), line[12:16].strip())
                s2 = '%s/%s/%s' % (line[51], line[52:57].strip(), line[42:46].strip())
                distname = pfx + 'LINK'
                cmd.distance(distname, s1, s2)
            elif line.startswith('SSBOND'):
                selename = pfx + 'SSBOND'
                selenames.add(selename)
                selestr = '%s & (chain %s & resi %s | chain %s & resi %s) & name CA+CB+SG'
                selestr = selestr % (name, line[15], line[17:22], line[29], line[31:36])
                cmd.select(selename, selestr, 0, 1, 1)
            elif line.startswith('HET '):
                # TODO
                pass

    if nice:
        allsites = ' '.join(selenames)
        cmd.show_as('cartoon', selection)
        cmd.show('lines', '(%s) and not polymer' % (selection))
        cmd.show('nonbonded', '(%s) and not polymer' % (selection))
        cmd.show('sticks', '(%s) and (%s)' % (selection, allsites))
        cmd.show('nb_spheres', '(%s) and (%s)' % (selection, allsites))
        cmd.show('dashes', '*LINK')
        cmd.color('gray', selection)
        for i, selename in enumerate(selenames):
            cmd.color(i+2, '(%s) and (%s)' % (selection, selename))

cmd.extend('select_sites', select_sites)

cmd.auto_arg[0]['select_sites'] = cmd.auto_arg[0]['pseudoatom']

# vi:expandtab:smarttab:sw=4
