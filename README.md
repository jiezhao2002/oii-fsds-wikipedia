# oii-fsds-wikipedia
A repository for downloading wikipedia revisions. Used in Fundamentals of Social Data Science for the MSc Social Data Science at the Oxford Internet Institute

## Installation
The dependencies can be installed using `pip`:
```bash
pip install .
```

NB: Remember to use some kind of virtual environment to avoid a world of pain!

## Usage
The script `download_wiki_revisions.py` will download xml-files for the last `n` revisions of a given wikipedia page. It has the following usage:
```bash
usage: download_wiki_revisions.py [-h] [--limit LIMIT] page

Download Wikipedia page revisions

positional arguments:
  page           Title of the Wikipedia page

options:
  -h, --help     show this help message and exit
  --limit LIMIT  Number of revisions to download (default: 10)
  --update       Instruct whether to update the current revisions (default:False)
```