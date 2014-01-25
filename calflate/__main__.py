# -*- encoding: utf-8 -*-

# AUTHOR: http://www.christoph-polcin.com
# LICENSE: FreeBSD License
# CREATED: 2014-01-25

from . import calflate
from copy import deepcopy
from optparse import OptionParser
from os import (path, environ)
# pylint: disable=F0401
try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser
# pylint: enable=F0401


def run():
    parser = OptionParser()
    parser.add_option(
        '-c', '--config', metavar='FILE',
        help='custom config file path', dest='config')
    parser.add_option(
        '-i', '--input', metavar='FILE',
        help='import from file', dest='input')
    parser.add_option(
        '-l', '--list', action='store_true', default=False,
        help='list collections')
    parser.add_option(
        '-n', '--dry-drun', action='store_true', default=False,
        help='dry run', dest='dryrun')
    parser.add_option(
        '-p', '--purge', action='store_true', default=False,
        help='purge orphan items')
    parser.add_option(
        '-v', '--verbose', action='store_true', default=False,
        help='verbose')

    items = _get_collection_set(*_get_config(parser.parse_args()[0]))
    for name, src, dst, opts in items:
        print('collection: %s' % name)
        if opts.input:
            src = (opts.input, None, None)
        if opts.list or opts.verbose:
            print('SRC: %s' % src[0])
            print('DST: %s' % dst[0])
            if opts.list:
                continue
        calflate(src, dst, opts)


def _get_collection_set(cfg, options):
    '''yields name, src, dst, opts'''
    def _v(section, key, val=None):
        try:
            return cfg.get(section, key)
        except:
            pass
        return val

    for s in cfg.sections():
        if cfg.has_option(s, 'src') and cfg.has_option(s, 'dst'):
            opts = deepcopy(options)
            for key in cfg.options(s):
                if key.startswith('src') or key.startswith('dst'):
                    continue
                v = cfg.get(s, key)
                vl = v.lower()
                if vl == 'true':
                    v = True
                elif vl == 'false':
                    v = False
                elif vl == 'none':
                    v = None
                elif v.isdigit():
                    v = float(v)

                setattr(opts, key, v)

            yield s, \
                (_v(s, 'src'), _v(s, 'src_user'), _v(s, 'src_pass')), \
                (_v(s, 'dst'), _v(s, 'dst_user'), _v(s, 'dst_pass')), \
                opts

    raise StopIteration


def _get_config(options):
    c = ConfigParser()
    c.read(['calflate.cfg', path.expanduser('~/.config/calflate.cfg')])
    if 'CALFLATE_CONFIG' in environ:
        c.read(path.expanduser(environ['CALFLATE_CONFIG']))
    if options.config:
        c.read(path.expanduser(options.config))
    delattr(options, 'config')
    return c, options


if __name__ == '__main__':
    run()
