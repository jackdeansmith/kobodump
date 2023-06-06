# Kobodump 

Kobodump is a python command line tool for dumping hilights and annotations from a Kobo reader .sqlite database to plain text markdown files. 

## Install

Install kobodump directly from this repo by running: 

```
$ python -m pip install "git+https://github.com/jackdeansmith/kobodump"
```

You can then run kobodump directly:
```
$ muntertool --help
```

## Usage 

```
Usage: kobodump [OPTIONS] DB_FILE OUTPUT_DIRECTORY

  Extracts highlights and annotations from the kobo sqlite database file
  DB_FILE and writes them to OUTPUT_DIRECTORY as .md files

Options:
  --help  Show this message and exit.
```

Kobodump will write markdown files to the output directory for each book.
