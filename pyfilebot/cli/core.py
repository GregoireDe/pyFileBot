#!/usr/bin/env python

from __future__ import absolute_import
from pyfilebot.cli.helpers import do_rename, do_rollback, iter_files, DEFAULT_RULES

from pyfilebot.utils import Files
from pyfilebot.main import Cache, Movie, ShowEpisode

import click


def option_dirs(func):
    func = click.option('-c', '--clean', is_flag=True, help='Clean empty dirs at the end', default=False)(func)
    func = click.option('-r', '--recursive', is_flag=True, help='Recursively lookup files in the director(y|ies)',
                        default=False)(func)
    return func


def option_renamer(func):
    func = click.option('-l', '--language', is_flag=True, help=f'Output language file for {func.__name__}',
                        default=False)(func)
    func = click.option('-d', '--dry-run', is_flag=True, help='Dry run your renaming', default=False)(func)
    func = click.option('-f', '--force', is_flag=True,
                        help='Force renaming if an output file already exists, skip otherwise', default=False)(func)
    func = click.option('-i', '--ignore', is_flag=True, help=f'Ignore {func.__name__} not found',
                        default=False)(func)
    func = click.option('-s', '--symlink', is_flag=True, default=False,
                        help="Create symbolic links instead of moving the files.(Unix Only)")(func)
    func = click.option('-u', '--rules', help='Format to apply for renaming',
                        default=DEFAULT_RULES[func.__name__], show_default=True)(func)
    func = click.option('-o', '--output',
                        help='The directory to move renamed files to, if not specified the input working directory is used')(
        func)
    return func


@click.group()
def cli():
    pass


@cli.command()
@option_dirs
@option_renamer
@click.argument('input', nargs=-1, required=True)
def movies(**args):
    """Rename movies from INPUT files or folders"""
    args["c"] = None
    iter_files(do_rename, cls=Movie, cache=None, **args)


@cli.command()
@option_dirs
@option_renamer
@click.argument('input', nargs=-1, required=True)
def shows(**args):
    """Rename TV shows from INPUT files or folders"""
    iter_files(do_rename, cls=ShowEpisode,  cache=Cache(), **args)


@cli.command()
@option_dirs
@click.argument('input', nargs=-1, required=True)
def rollback(**args):
    """Rollback INPUT files or folders based on the history"""
    iter_files(do_rollback, **args)


@cli.command()
def history():
    """History of files renamed"""
    Files.read_history()
