#!/usr/bin/env python

import traceback

from pyfilebot.utils import Files

CONTEXT_SETTINGS = {'context_settings': dict(help_option_names=['-h', '--help'])}

DEFAULT_RULES = {
    "movies": "{n} ({y})/{n} ({y}).{x}",
    "shows": "{n}/Season {s}/{n} - S{s00}E{e00} - {t}.{x}"
}


def do_rename(file_path: str,  **kw: any):
    """Perform a  renaming on a file media

   Args:
       file_path (str): File path to rename
       kw (**any): Parameters and functions to use
   """
    try:
        file = kw['cls'](file_path, kw['ignore'], kw['language'], kw['cache'])
        new_name = Files.process_rules(kw['rules'], kw['cls'].__name__, file.__dict__)
        Files.rename(file_path, kw['output'], new_name, kw['force'], kw['action'], kw['dry_run'])
    except Exception as e:
        print(e)


def do_rollback(file_path: str, **kw: any):
    """Perform a  renaming on a file media

   Args:
       file_path (str): File path to rollback
       kw (**any): Parameters and functions to use
   """
    Files.rollback(file_path)


def iter_files(func: callable, **kw: any):
    """Perform an action on each file in input and clean directory if specified

      Args:
          func (func): Operation to apply
          kw (**any): Parameters and functions to use
      """
    [func(file_path, **kw) for i in kw['input'] for file_path in Files.list(i, kw['recursive'])]
    [Files.remove_empty_folders(i) for i in kw['input'] if kw['clean']]
