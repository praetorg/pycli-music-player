#!/usr/bin/env python

def music_format(filename):
    item = str(open(filename, "rb").read(32))
    if 'mp4' in item:
        musicformat = 'aac'
    elif 'Ogg' in item:
        musicformat = 'ogg'
    elif 'ID3' in item:
        musicformat = 'mp3'
    else:
        musicformat = None

    return musicformat