#!/usr/bin/env python

from __future__ import absolute_import

from pyfilebot.utils import Files

DEFAULT_RULES = {
    "movies": "{title} ({year}).{ext}",
    "shows": "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
}


def do_rename(old_path, old_name, **args):
    file = args['cls'](old_name, args['ignore'], args['language'], args['cache'])
    new_name = Files.process_rules(args['rules'], file)
    Files.rename(old_path, args['output'], new_name, args['force'], args['symlink'], args['dry_run'])


def do_rollback(old_path, **args):
    Files.rollback(old_path)


def iter_files(func, **args):
    [func(old_path, old_name, **args) for i in args['input'] for old_path, old_name in Files.list(i, args['recursive'])]
