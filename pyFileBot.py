#!/usr/bin/env python

import os
import argparse
from utils.files import Files
from utils.data import Store, Movie, ShowEpisode

DEFAULT_RULES = {
    "movies": "{title} ({year}).{ext}",
    "shows": "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
}

DEFAULT_ACTION = {
    "movies": "Movie",
    "shows": "ShowEpisode"
}


def main():
    parser = argparse.ArgumentParser(description='pyFileBot')

    subparsers = parser.add_subparsers(help='Action to perform', dest='action')
    subparsers.required = True
    choices_parser = argparse.ArgumentParser(add_help=False)
    movies = subparsers.add_parser('movies', help='Rename movies', parents=[choices_parser],
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    shows = subparsers.add_parser('shows', help='Rename TV shows', parents=[choices_parser],
                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    rollback = subparsers.add_parser('rollback', help='Rollback files/folders based on the history',
                                     parents=[choices_parser],
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    history = subparsers.add_parser('history', help='History of files renamed', parents=[choices_parser],
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    for name, subp in subparsers.choices.items():
        if name in ["movies", "shows", "rollback"]:
            subp.add_argument('input', help='Input dirs/files to scan', nargs='*', type=str)
            subp.add_argument('-r', '--recursive', help='Scan input dir recursively', action="store_true",
                              default=False)
            subp.add_argument('-c', '--clean', help='Clean empty dirs at the end', action="store_true", default=False)

        if name in ["movies", "shows"]:
            subp.add_argument('-o', '--output',
                              help='The directory to move renamed files to, if not specified the file working directory is used.',
                              default=False)
            subp.add_argument('-u', '--rules', help='Format to apply for renaming', type=str,
                              default=DEFAULT_RULES[name])
            subp.add_argument('-l', '--language', help=f'Output language file for the {name}', action="store_true",
                              default="en")
            subp.add_argument('-f', '--force', help='Force renaming if an output file already exists',
                              action="store_true", default=False)
            subp.add_argument('-i', '--ignore', help=f'Ignore {name} not found', action="store_true", default=False)


    args = vars(parser.parse_args())

    print(f"*** pyFileBot > {args['action'].capitalize()} ***\n")


    if "history" in args['action']:
        Files.read_history()

    else:
        c = Store() if "shows" in args['action'] else None
        for i in args['input']:
            for old_path, old_name in Files.list(i, args['recursive']):
                if "rollback" in args['action']:
                    Files.rollback(old_path)
                else:
                    cls = globals()[DEFAULT_ACTION[args['action']]]
                    file = cls(old_name, args['ignore'], c)
                    new_name = Files.process_rules(args['rules'], file)
                    Files.move(old_path, args['output'], new_name, args['force'])
            if args['clean']:
                Files.remove_empty_folders(i)


if __name__ == "__main__":
    main()
