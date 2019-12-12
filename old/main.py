#!/usr/bin/env python

from __future__ import absolute_import

import argparse
import click
from utils.files import Files
from utils.data import Cache, ShowEpisode, Movie

DEFAULT_RULES = {
    "movies": "{title} ({year}).{ext}",
    "shows": "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
}

DEFAULT_ACTION = {
    "movies": "Movie",
    "shows": "ShowEpisode"
}


def option_dirs(func):
    func = click.option('-c', '--clean', is_flag=True, help='Clean empty dirs at the end', default=False)(func)
    func = click.option('-r', '--recursive', is_flag=True, help='Recursively lookup files in the director(y|ies)', default=False)(func)
    return func


def option_renamer(func):
    func = click.option('-l', '--language', is_flag=True, help=f'Output language file for {func.__name__}',
                        default=False)(func)
    func = click.option('-d', '--dry-run', is_flag=True, help='Dry run your renaming', default=False)(func)
    func = click.option('-f', '--force', is_flag=True,
                        help='Force renaming if an output file already exists, skip otherwise', default=False)(func)
    func = click.option('-i', '--ignore', is_flag=True, help=f'Ignore {func.__name__} not found',
                        default=False)(func)
    func = click.option('-u', '--rules', help='Format to apply for renaming',
                        default=DEFAULT_RULES[func.__name__], show_default=True)(func)
    func = click.option('-o', '--output',
                        help='The directory to move renamed files to, if not specified the input working directory is used')(func)
    return func


@click.group()
def cli():
    pass


@cli.command()
@option_dirs
@option_renamer
@click.argument('input', nargs='-1', required=True)
def movies(**args):
    """Rename movies"""
    args["c"] = None
    iter_files(do_rename, type="Movie", **args)


@cli.command()
@option_dirs
@option_renamer
@click.argument('input', nargs=-1, required=True)
def shows(**args):
    """Rename TV shows"""
    args["c"] = Cache()
    iter_files(do_rename, type="ShowEpisode", **args)


@cli.command()
@option_dirs
@click.argument('input', nargs=-1, required=True)
def rollback(**args):
    """Rollback files/folders based on the history"""
    iter_files(do_rollback, **args)


@cli.command()
def history():
    """History of files renamed"""
    Files.read_history()


def do_rename(old_path, old_name, **args):
    cls = globals()[args['type']]
    file = cls(old_name, args['ignore'], args['language'], args['c'])
    new_name = Files.process_rules(args['rules'], file)
    Files.move(old_path, args['output'], new_name, args['force'], args['dry_run'])


def do_rollback(old_path, **args):
    Files.rollback(old_path)


def iter_files(func, **args):
    [func(old_path, old_name, **args) for i in args['input'] for old_path, old_name in Files.list(i, args['recursive'])]


if __name__ == "__main__":
    cli()
