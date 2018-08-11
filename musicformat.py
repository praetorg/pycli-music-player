#!/usr/bin/env python

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
    elif item.startswith('52494646') and item[16:].startswith('57415645'):
        return 'wav'
    else:
        return None