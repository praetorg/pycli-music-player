#!/usr/bin/env python

def musicFormat(filename):
    item = str(open(filename, "rb").read(32))
    if item[18:].startswith('ftypisom') or item[18:].startswith('ftypM4A'):
        return 'aac'
    elif item[3:].startswith('OggS'):
        return 'ogg'
    elif item[3:].startswith('ID3'):
        return 'mp3'
    elif item[3:].startswith('fLaC'):
        return 'flac'
    else:
        return None


def musicFormatHex(filename):
    item = str(open(filename, "rb").read(32).hex())
    if item[8:].startswith('667479704d344120') or item[8:].startswith('6674797069736f6d'):
        return 'aac'
    elif item.startswith('4f676753'):
        return 'ogg'
    elif item.startswith('494433'):
        return 'mp3'
    elif item.startswith('664c6143'):
        return 'flac'
    else:
        return None