import argparse
import csv
from dataclasses import dataclass
import re
from pathlib import Path

import json5
import requests
from tqdm import tqdm


@dataclass
class Track:
    name: str
    link: str


def download_track_core(track_link: str, dest_file: Path, counter_status: str):
    BASE_URLS = ['https://files01.tokybook.com/audio/',  'https://files02.tokybook.com/audio/']

    response = None

    for base_url in BASE_URLS:
        response = requests.get(base_url + track_link, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kb

            t = tqdm(total=total_size, unit='iB', unit_scale=True)
            t.set_description(counter_status)

            with open(dest_file, 'wb') as f:
                for data in response.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
            t.close()

            return True
        
    print('[FAILED] Failed to download track: ', counter_status)
    print(response.text if response else 'No response')
    return False

def download_track(track_name: str, track_link: str, dest_dir: Path, counter_status: str):
    track_file = dest_dir / (track_name + '.mp3')
    downloaded = download_track_core(track_link, track_file, counter_status)

def extract_tracks_info(web_page_response: str) -> list[Track]:
    match = re.search(r"tracks\s*=\s*(\[[^\]]+\])\s*", web_page_response)

    if match is None:
        raise RuntimeError('Could not find tracks info.')

    match_group = match.group(1)
    tracks_raw = json5.loads(match_group)

    # Should contain:
    # track: int
    # name: str
    # chapter_link_dropbox: str (url)
    # duration: int
    # chapter_id: int
    # post_id: int
    #
    # For debugging:
    # from pprint import pprint
    # pprint(tracks_raw)

    if not isinstance(tracks_raw, list):
        raise RuntimeError('Could not parse json: {}'.format(match_group))

    # First track is the 'welcome audio' from tokybook.
    tracks_raw.pop(0)
    
    tracks = [Track(x['name'], x['chapter_link_dropbox']) for x in tracks_raw]
    return tracks


if __name__ == '__main__':
    parser = argparse.ArgumentParser("tokydl")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='Url from tokybook, e.g. https://tokybook.com/empire-of-storms', default=argparse.SUPPRESS)
    group.add_argument('--file', help='CSV file containing | name | link |, as taken from tracks.log', default=argparse.SUPPRESS)
    parser.add_argument('--dest', help='Output directory', default='./media')
    args = parser.parse_args()
    
    if 'url' in args:
        print('Getting page content...')
        toky_response = requests.get(args.url).text

        print('Extracting track info...')
        tracks = extract_tracks_info(toky_response)

        # Write tracks to file for partial recovery if necessary
        print('Writing tracks.log...')
        with open('tracks.log', 'a') as f:
            writer = csv.writer(f)
            writer.writerows([(x.name, x.link) for x in tracks])
    else:
        print('Reading tracks from file')
        with open(args.f, 'r') as f:
            reader = csv.reader(f)
            tracks = [Track(x[0], x[1]) for x in reader]

    # Setup download directory
    dest_dir = Path(args.dest)
    dest_dir.mkdir(exist_ok=True)
    
    for n,track in enumerate(tracks):
        counter_status = '{}/{}: "{}"'.format(n, len(tracks), track.name)
        download_track(track.name, track.link, dest_dir, counter_status)
