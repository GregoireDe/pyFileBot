#!/usr/bin/env python

from __future__ import absolute_import


DEFAULT_RULES = {
    "movies": "{title} ({year}).{ext}",
    "shows": "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
}

DEFAULT_ACTION = {
    "movies": "Movie",
    "shows": "ShowEpisode"
}


def do_rename(old_path, old_name, **args):
    cls = globals()[args['type']]
    file = cls(old_name, args['ignore'], args['language'], args['c'])
    new_name = Files.process_rules(args['rules'], file)
    Files.move(old_path, args['output'], new_name, args['force'], args['dry_run'])


def do_rollback(old_path, **args):
    Files.rollback(old_path)


def iter_files(func, **args):
    [func(old_path, old_name, **args) for i in args['input'] for old_path, old_name in Files.list(i, args['recursive'])]


