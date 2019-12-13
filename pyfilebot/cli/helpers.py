#!/usr/bin/env python

from __future__ import absolute_import

from pyfilebot.utils import Files

CONTEXT_SETTINGS = {'context_settings': dict(help_option_names=['-h', '--help'])}

DEFAULT_RULES = {
    "movies": "{title} ({year}).{ext}",
    "shows": "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
}


def do_rename(old_path, old_name, **args):
    try:
        file = args['cls'](old_name, args['ignore'], args['language'], args['cache'])
        new_name = Files.process_rules(args['rules'], file)
        Files.rename(old_path, args['output'], new_name, args['force'], args['action'], args['dry_run'])
    except Exception as e:
        print(e)


def do_rollback(old_path, **args):
    Files.rollback(old_path)


def iter_files(func, **args):
    [func(old_path, old_name, **args) for i in args['input'] for old_path, old_name in Files.list(i, args['recursive'])]
