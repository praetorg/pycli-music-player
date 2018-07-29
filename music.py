#!/usr/bin/env python
from pathlib import Path
import os
import sys
import shutil
import random
import subprocess
import musicformat


HELPER = """
By default, play all music from ~/Music folder, else play supplied directory or file.
>music 'argument(s)' 'path'
Arguments:
    '-r','--repeat': Repeat all songs indefinitely
    '-s','--shuffle': Shuffle all songs
Short arguments may be combined, such as '-rs'.
Ctrl-c to exit.
"""


def main(filename=None, shuffle=False, repeat=False):
    if filename:
        music = filename
    else:
        music = os.path.join(Path.home(), 'Music')
    songs = list()
    if os.path.isdir(music):
        for root, dirs, files in os.walk(music):
            for name in files:
                songs.append(os.path.join(root, name))
    else:
        if os.path.isabs(music):
            songs.append(music)
        else:
            songs.append(os.path.join(os.getcwd(), music))
    if shuffle:
        random.shuffle(songs)
    for song in songs:
        try:
            form = musicformat.music_format(song)
            if form is None:
                print(f'Discarding file, not a known music format: {song}')
                songs.pop(song)
                continue
            print(f'Playing song: {song}')      
            play(song)
        except FileNotFoundError:
            print('File not found, skipping.')
    if repeat and len(songs) > 0:
        main(filename, shuffle, repeat)
    else:
        print('Done, no more files.')


def play(song):
    command = f'{PLAYER} -nodisp -autoexit -hide_banner "{song}"'
    subprocess.call(command, shell=True, bufsize=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)


def get_player():
    if shutil.which("avplay"):
        return "avplay"
    elif shutil.which("ffplay"):
        return "ffplay"
    else:
        print("ffmpeg or avconf not found, exiting.")
        exit()


PLAYER = get_player()


if __name__ == '__main__':
    shuffle = False
    repeat = False
    filename = None
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "--?" in sys.argv:
            print(HELPER)
            exit()
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                if '--' in arg:
                    if "--shuffle" in arg:
                        shuffle = True
                    if "--repeat" in arg:
                        repeat = True
                if 's' in arg:
                    shuffle = True
                if 'r' in arg:
                    repeat = True
            else:
                filename = arg
    try:
        main(filename, shuffle, repeat)
    except KeyboardInterrupt:
        print('\r\nExiting.')
        exit()
