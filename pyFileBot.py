#!/usr/bin/env python

import os
import argparse
from utils.files import Files
from utils.data import Store, Movie, ShowEpisode


def main():
    parser = argparse.ArgumentParser(description='pyFileBot', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', help='Input dirs/files to scan', nargs='+', type=str)
    parser.add_argument('-o', '--output_dir', help='Output directory to move files', default=False)
    parser.add_argument('-u', '--output_rules', help='Rules to apply for renaming', type=str, default=None)
    parser.add_argument('-l', '--language', help='Output language file name/show',
                        action="store_true", default="en")
    parser.add_argument('-m', '--movies', help='Using Movies renammer instead of TV shows',
                        action="store_true", default=False)
    parser.add_argument('-f', '--output_force', help='Force renaming if an output file already exists',
                        action="store_true", default=False)
    parser.add_argument('-i', '--ignore', help='Ignore show/movie not found',
                        action="store_true", default=False)
    parser.add_argument('-c', '--clean', help='Clean empty dirs at the end', action="store_true",
                        default=False)
    parser.add_argument('-r', '--recursiv', help='Scan input dir recursively', action="store_true",
                        default=False)
    args = vars(parser.parse_args())

    s = Store()

    print("*** pyFileBot running ***")

    if not args['movies']:
        s = Store()
        if not args["output_rules"]:
            args["output_rules"] = "{show_title}/Season {season}/{show_title} - S{season_0}E{episode_0} - {title}.{ext}"
    else:
        if not args["output_rules"]:
            args["output_rules"] = "{title} ({year}).{ext}"

    for i in args['input']:
        for old_path, old_name in Files.list(i, args['recursiv']):
            if args['movies']:
                file = Movie(old_name, args['ignore'])
            else:
                file = ShowEpisode(s, old_name, args['ignore'])
            new_name = Files.process_rules(args['output_rules'], file)
            Files.move(old_path, args['output_dir'], new_name, args['output_force'])

        if args['clean']:
            Files.remove_empty_folders(i)


if __name__ == "__main__":
    main()
