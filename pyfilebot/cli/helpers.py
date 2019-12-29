#!/usr/bin/env python

from __future__ import absolute_import

from pyfilebot.utils import Files

CONTEXT_SETTINGS = {'context_settings': dict(help_option_names=['-h', '--help'])}

DEFAULT_RULES = {
    "movies": "{t} ({y})/{t} ({y}).{x}",
    "shows": "{t}/Season {s}/{t} - S{s00}E{e00} - {n}.{x}"
}


def do_rename(filepath, filename, **args):
    try:
        file = args['cls'](filename, args['ignore'], args['language'], args['cache'])
        new_name = Files.process_rules(args['rules'],args['cls'].__class__.__name__, file)
        Files.rename(filepath, args['output'], new_name, args['force'], args['action'], args['dry_run'])
    except Exception as e:
        print(e)


def do_rollback(old_path, **args):
    Files.rollback(old_path)


def iter_files(func, **args):
    [func(filepath, filename, **args) for i in args['input'] for filepath, filename in Files.list(i, args['recursive'])]
