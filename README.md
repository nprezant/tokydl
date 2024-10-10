# tokydl

A tokybook downloader

Download audiobooks from tokybook.

## Usage

```bash
$ python tokydl.py --help
usage: tokydl [-h] (--url URL | --file FILE)

options:
  -h, --help   show this help message and exit
  --url URL    Url from tokybook, e.g. https://tokybook.com/empire-of-storms
  --file FILE  File containing | name | link |, as taken from tracks.log
  --dest DEST  Output directory
```

## Install

Requirements

```bash
pip install -r requirements.txt
```

## Running

```bash
git clone https://github.com/nprezant/tokydl.git
cd tokydl
pip install -r requirements.txt
python tokydl.py --url https://tokybook.com/empire-of-storms # downloaded files will be written to ./media
```

## Tips

If your audiobook download is interrupted, you can copy/edit the `tracks.log` file to download only the files you need, rather than re-downloading the whole book. `tracks.log` will contain a running list of all tracks that `tokydl` attempts to download.

```bash
python tokydl.py --file tracks.log
```
