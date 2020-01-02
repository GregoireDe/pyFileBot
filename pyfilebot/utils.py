#!/usr/bin/env python
import os
import shutil
import re
import tempfile

import string
import socket

from random import choice, seed
from datetime import datetime

seed(socket.gethostname())
TEMP_HISTORY_FILE = os.path.join(tempfile.gettempdir(), ''.join([choice(string.ascii_letters) for n in range(12)]))

SPECIAL_RULES = {
    "plex": {"Movie": "{n} ({y})/{n} ({y}).{x}",
             "ShowEpisode": "{n}/Season {s}/{n} - S{s00}E{e00} - {t}.{x}"}
}


class Files:

    @staticmethod
    def remove_empty_folders(path, remove_root=True):
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
    def list(start_path, recur=True):
        extensions = ['avi', 'flv', 'm4v', 'mkv', 'mp4', 'mov', 'mpg', 'mpeg', 'wmv', 'srt']
        if os.path.isfile(start_path):
            yield start_path, os.path.basename(start_path)
        else:
            for dirpath, dirs, files in os.walk(start_path, topdown=True):
                for file in files:
                    absolute_path = os.path.abspath(os.path.join(dirpath, file))
                    ext = absolute_path.split('.')[-1]
                    if ext in extensions:
                        yield absolute_path, file
                if not recur:
                    break

    @staticmethod
    def process_rules(name, type, details):
        try:
            for r in SPECIAL_RULES.keys():
                if r == name:
                    name = SPECIAL_RULES[name][type]
            name = name.format(**details)
            return re.sub(r'[*?:"<>|]', "", name)
        except KeyError as e:
            raise Exception(e)

    @staticmethod
    def rename(source_filepath, output_dir, dest_filename, force, action, dry_run):
        try:
            dest_filepath = os.path.abspath(os.path.join(os.path.dirname(source_filepath), dest_filename))
            if output_dir:
                dest_filepath = os.path.abspath(os.path.join(output_dir, dest_filename))
            if source_filepath == dest_filepath or (os.path.isfile(dest_filepath) and not force):
                print(f"File skipped (already exists): {dest_filepath}")
                return
            if os.path.isfile(dest_filepath) and force:
                os.remove(dest_filepath)
            if not dry_run:
                os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)
                if action == "sym":
                    os.symlink(source_filepath, dest_filepath)
                elif action == "copy":
                    shutil.copy2(source_filepath, dest_filepath)
                else:
                    shutil.move(source_filepath, dest_filepath)
                Files.write_history(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{source_filepath};{dest_filepath}\n")
            print(f"{source_filepath}\n> {dest_filepath}\n")
        except Exception as e:
            print(f"{e}")

    @staticmethod
    def write_history(content):
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
    def rollback(old_path):
        print(old_path)
        with open(TEMP_HISTORY_FILE, 'r') as f:
            content = f.readlines()
        content.reverse()
        for i, line in enumerate(content):
            i_date, i_old_path, i_new_path = line.split(";")
            if i_new_path.strip() == old_path:
                os.makedirs(os.path.dirname(i_old_path), exist_ok=True)
                shutil.move(old_path, i_old_path)
                # Removing lines
                content.remove(line)
                with open(TEMP_HISTORY_FILE, "w") as f:
                    content.reverse()
                    f.writelines(content)
                print(f"{old_path}\n> {i_old_path}")
                break
