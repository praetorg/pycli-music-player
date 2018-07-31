#!/usr/bin/env python

## TODO: use magic strings to cover edgecases

def music_format(filename):
    item = str(open(filename, "rb").read(32))
    if 'mp4' in item:
        return 'aac'
    elif 'Ogg' in item:
        return 'ogg'
    elif 'ID3' in item:
        return 'mp3'
    elif 'fLaC' in item:
        return 'flac'
    else:
        return None