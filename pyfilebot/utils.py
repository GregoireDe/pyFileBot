#!/usr/bin/env python

import os
import shutil
import re
import tempfile

import glob

import string
import socket

from random import choice, seed
from datetime import datetime
from typing import Iterable

seed(socket.gethostname())
TEMP_HISTORY_FILE = os.path.join(tempfile.gettempdir(), ''.join([choice(string.ascii_letters) for n in range(12)]))

SPECIAL_RULES = {
    "plex": {"Movie": "{n} ({y})/{n} ({y}).{x}",
             "ShowEpisode": "{n}/Season {s}/{n} - S{s00}E{e00} - {t}.{x}"}
}
DEFAULT_RULES = {
    "movies": "{n} ({y})/{n} ({y}).{x}",
    "shows": "{n}/Season {s}/{n} - S{s00}E{e00} - {t}.{x}"
}


class Files:

    @staticmethod
    def remove_empty_folders(path: str, remove_root: bool = True):
        g = glob.glob(path)
        if g:
            path = os.path.dirname(path[0])
        if not os.path.isdir(path):
            return
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    Files.remove_empty_folders(fullpath)
        files = os.listdir(path)
        if len(files) == 0 and remove_root:
            os.rmdir(path)

    @staticmethod
    def list(start_path: str, recur: bool = True) -> Iterable:
        extensions = ['avi', 'flv', 'm4v', 'mkv', 'mp4', 'mov', 'mpg', 'mpeg', 'wmv', 'srt', 'nfo']
        g = glob.glob(start_path)
        if g and (len(g) > 1 or os.path.isfile(g[0])):
            for file_path in g:
                ext = file_path.split('.')[-1]
                if ext in extensions:
                    yield file_path
        else:
            if os.path.isfile(start_path):
                yield start_path
            else:
                for dirpath, dirs, files in os.walk(start_path, topdown=True):
                    for file in files:
                        file_path = os.path.abspath(os.path.join(dirpath, file))
                        ext = file_path.split('.')[-1]
                        if ext in extensions:
                            yield file_path
                    if not recur:
                        break

    @staticmethod
    def process_rules(name: str, type: str, details: dict) -> str:
        try:
            for r in SPECIAL_RULES.keys():
                if r == name:
                    name = SPECIAL_RULES[name][type]
            name = name.format(**details)
            return re.sub(r'[*?:"<>|]', "", name)
        except KeyError as e:
            raise Exception(e)

    @staticmethod
    def rename(file_path: str, out_dir: str, out_filename: str, force: bool, action: str, dry_run: bool):
        try:
            out_file_path = os.path.abspath(os.path.join(os.path.dirname(file_path), out_filename))
            if out_dir:
                out_file_path = os.path.abspath(os.path.join(out_dir, out_filename))
            if file_path == out_file_path or (os.path.isfile(out_file_path) and not force):
                print(f"File skipped (already exists): {out_file_path}")
                return
            if not dry_run:
                if os.path.isfile(out_file_path) and force:
                    os.remove(out_file_path)
                os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                if action == "sym":
                    os.symlink(file_path, out_file_path)
                elif action == "copy":
                    shutil.copy2(file_path, out_file_path)
                else:
                    shutil.move(file_path, out_file_path)
                Files.write_history(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{file_path};{out_file_path}\n")
            print(f"{file_path}\n> {out_file_path}\n")
        except Exception as e:
            print(f"{e}")

    @staticmethod
    def write_history(content: str):
        with open(TEMP_HISTORY_FILE, 'a') as f:
            f.write(content)

    @staticmethod
    def read_history():
        if os.path.isfile(TEMP_HISTORY_FILE):
            with open(TEMP_HISTORY_FILE, 'r') as f:
                c = f.readlines()
                c.reverse()
            for i, line in enumerate(c):
                i_date, i_old_file, i_new_file = line.split(";")
                print(f"{i_date}:\n{i_old_file}\n> {i_new_file}")
        else:
            print(f"No history")

    @staticmethod
    def rollback(file_path: str):
        print(file_path)
        with open(TEMP_HISTORY_FILE, 'r') as f:
            content = f.readlines()
        content.reverse()
        for i, line in enumerate(content):
            i_date, i_old_path, i_new_path = line.split(";")
            if i_new_path.strip() == file_path:
                os.makedirs(os.path.dirname(i_old_path), exist_ok=True)
                shutil.move(file_path, i_old_path)
                # Removing lines
                content.remove(line)
                with open(TEMP_HISTORY_FILE, "w") as f:
                    content.reverse()
                    f.writelines(content)
                print(f"{file_path}\n> {i_old_path}")
                break
