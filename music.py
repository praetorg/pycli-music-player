#!/usr/bin/env python
from pathlib import Path
import os
import sys
import shutil
import random
import subprocess
import threading
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

HELPER2 = """
pycli-music console commands:
    's', 'skip', 'n', 'next': Next song
    'p', 'prev', 'b', 'back': Previous song
    'x', 'exit', 'q', 'quit': Exit player
    'repeat'                : Toggle repeat
    'shuffle'               : Toggle shuffle
"""


MUSICPROCESS = None


def main():
    while True:
        song = start.current()
        play(song)
        start.next()


class Songs:
    def __init__(self, filename=None, shuffle=False, repeat=False):
        self.songs = list()
        self.counter = 0
        self.repeat = repeat
        self.filename = filename
        self.shuffle = shuffle
        if filename:
            music = filename
        else:
            music = os.path.join(Path.home(), 'Music')
        if os.path.isdir(music):
            for root, dirs, files in os.walk(music):
                for name in files:
                    self.songs.append(os.path.join(root, name))
        else:
            if os.path.isabs(music):
                self.songs.append(music)
            else:
                self.songs.append(os.path.join(os.getcwd(), music))
        for song in self.songs:
            try:
                form = musicformat.music_format(song)
                if form is None:
                    self.songs.pop(song)
            except FileNotFoundError:
                self.songs.pop(song)
        if len(self.songs) < 1:
            print('\r\nNo valid files to play.')
            shutdownfn()
        if shuffle:
            self.shufflefn()


    def next(self):
        if self.counter < len(self.songs) - 1:
            self.counter+=1
        elif self.repeat:
            self.__init__(self.filename, self.shuffle, self.repeat)
        else:
            shutdownfn()


    def shufflefn(self):
        random.shuffle(self.songs)


    def previous(self):
        if self.counter > 0:
            self.counter-=2


    def current(self):
        return self.songs[self.counter]


    def repeat_toggle(self):
        self.repeat = not self.repeat
        if self.repeat:
            printout(f'Repeat on.')
        else:
            printout(f'Repeat off.')

    
    def shuffle_toggle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            printout(f'Shuffle on.')
            self.shufflefn()
        else:
            printout(f'Shuffle off.')


    def end(self):
        self.repeat = False
        self.counter = len(self.songs) - 1
        

def play(song):
    global MUSICPROCESS
    printout(f'Playing song: {song}')
    command = f'{PLAYER} -nodisp -autoexit -hide_banner "{song}"'
    MUSICPROCESS = subprocess.Popen(command, shell=True, bufsize=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)
    MUSICPROCESS.wait()


def console():
    try:
        while True:
            control = None
            control = input()
            if control == 'skip' or control == 'next' or control == 's' or control == 'n':
                MUSICPROCESS.terminate()
            elif control == 'exit' or control == 'quit' or control == 'x' or control == 'q':
                shutdownfn()
            elif control == 'back' or control == 'prev' or control == 'p' or control =='b':
                start.previous()
                MUSICPROCESS.terminate()
            elif control == 'help' or control == 'h' or control == '?':
                printout(HELPER2)
            elif control == 'repeat':
                start.repeat_toggle()
            elif control == 'shuffle':
                start.shuffle_toggle()
    except KeyboardInterrupt:
        shutdownfn()


def printout(statement):
    print(f'\r\n{statement}\r\npycli-music>>> ', end='')


def get_player():
    if shutil.which("avplay"):
        return "avplay"
    elif shutil.which("ffplay"):
        return "ffplay"
    else:
        printout("ffmpeg or avconf not found, exiting.")
        shutdownfn()


def shutdownfn():
    MUSICPROCESS.terminate()
    start.end()
    sys.exit()


PLAYER = get_player()


if __name__ == '__main__':
    shuffle = False
    repeat = False
    filename = None
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "--?" in sys.argv:
            printout(HELPER)
            shutdownfn()
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
        thread = threading.Thread(target=console)
        thread.start()
        start = Songs(filename, shuffle, repeat)
        main()
    except KeyboardInterrupt:
        shutdownfn()
