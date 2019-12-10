#!/usr/bin/env python
import os
import shutil
import re


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
    def process_rules(name, details):
        keys = re.findall(r"\{(\w+)\}", name)
        for key in keys:
            if key in list(details.__dict__.keys()):
                name = name.replace(f"{{{key}}}", str(getattr(details, key)))
            elif key == "season_0" or key == "episode_0":
                name = name.replace(f"{{{key}}}", str(getattr(details, key[:-2])).rjust(2, '0'))
            else:
                raise Exception(f"Unknown {key} variable")
        name = re.sub(r'[*?:"<>|]', "", name)
        return name

    @staticmethod
    def move(old_file, output_dir, new_name, output_force):
        if output_dir:
            new_file = os.path.abspath(os.path.join(output_dir, new_name))
        else:
            new_file = os.path.abspath(os.path.join(os.path.dirname(old_file), new_name))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        try:
            if old_file != new_file:
                if os.path.isfile(new_file):
                    if output_force:
                        os.remove(new_file)
                    else:
                        print(f"File skipped (already exists): {new_file}")
                        return
                shutil.move(old_file, new_file)
                print(f"{old_file}\n Renamed to: {new_file}")
        except Exception as e:
            print(f"{e}")
