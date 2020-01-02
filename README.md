# pyFileBot

> *Media file renamer using TheTVDB and IMDb databases.*


The tool is not based on  FileBot, but since it wasn't free and over featured for my needs, I developped my own. 


## In brief

- [Features](#features)
- [Installation](#installation)
- [Examples](#examples)
- [Comparative](#comparative)
- [License](#license)



## Features

- Manage **Movies** and **TV Shows**
- Handle **multiple** directories or files at once, even path with **wildcards**
- **Custom** output file format
- Choose between **copy, move or symlinks**
- Manage user input or pass on **unknown** files
- Keep an **history** and **rollback** in case of issue.

###### TODO

- Use logger
- 


## Installation

```text
$ pip install pyfilebot
```

## Examples

##### Check help menus to list all available options


```text
$ pyfilebot -h
Usage: pyfilebot [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help  Show this message and exit.

Commands:
  history   History of files renamed
  movies    Rename movies from INPUT files or folders
  rollback  Rollback INPUT files or folders based on the history
  shows     Rename TV shows from INPUT files or folders
```

```text
$ pyfilebot movies -h
Usage: pyfilebot movies [OPTIONS] INPUT...

  Rename movies from INPUT files or folders

Options:
  -r, --recursive               Recursively lookup files in the
                                director(y|ies)
  -c, --clean                   Clean empty dirs at the end
  -o, --output TEXT             The directory to move renamed files to, if not
                                specified the input working directory is used
  -u, --rules TEXT              Format to apply for renaming  [default:
                                {n}/Season {s}/{n} - S{s00}E{e00} - {t}.{ext}]
  -a, --action [move|copy|sym]  Use move, copy or symlink files to the
                                destination  [default: move]
  -i, --ignore                  Ignore shows not found, best choice for non-
                                interactive mode
  -f, --force                   Force renaming if an output file already
                                exists, ignore otherwise
  -d, --dry-run                 Dry run your renaming
  -l, --language TEXT           Output language file for shows  [default: en]
  -h, --help                    Show this message and exit.
```

## Rules

You can easily define your own episode and movie naming schemes. It uses Python format strings

| Bind  | Description  |
|-------|------------------|
| **n** | Movie / Show name |   
| **y** | Year air date |  
| **x** | File extension  |   
| **t** | Episode name |   
| **s** | Season  |   
| **s00** | Season (2 digits format)  |   
| **e** | Episode  |   
| **e00** | Episode (2 digits format)  |   


```text
$ pyfilebot shows --rules "{n}/Season {s}/{n} - S{s00}E{e00} - {t}.{x}" ...
Watchmen/Season 1/Watchmen - S01E01 - It's Summer and We're Running Out of Ice.mkv
```

##### Special

| Bind  | Description  |
|-------|------------------|
| **plex** | Rule recommended for plex media |   
```text
$ pyfilebot shows --rules plex ...
Watchmen/Season 1/Watchmen - S01E01 - It's Summer and We're Running Out of Ice.mkv

$ pyfilebot movies --rules plex ...
Ad Astra (2019)/Ad Astra (2019).mkv
```

