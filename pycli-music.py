#!/usr/bin/env python
from pathlib import Path
import os
import sys
import signal
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
    'k', 'skip', 'n', 'next': Next song
    'e', 'prev', 'b', 'back': Previous song
    'x', 'exit', 'q', 'quit': Exit player
    's', 'stop'             : Stop song
    'p', 'play'             : Play song
    'repeat'                : Toggle repeat
    'shuffle'               : Toggle shuffle
"""


def main():
    thread = threading.Thread(target=console)
    thread.daemon = True
    thread.start()
    try:
        while player.online():
            try:
                while player.playing():
                    printout(f'Playing song: {player.current()}')
                    player.playfn()
                    if player.complete():
                        player.next()
            except EndOfPlaylist:
                printout('End of playlist.')
    except PlayerNotFound:
        printout('FFmpeg or avconv not found.')
    except FileNotFoundError:
        printout('No valid files found.')
    finally:
        player.end()
        shutdownfn()


class EndOfPlaylist(Exception):
    pass


class PlayerNotFound(Exception):
    pass


class Player:
    def __init__(self, filename=None, shuffle=False, repeat=False):
        self.songs = list()
        self.counter = 0
        self.repeat = repeat
        self.filename = filename
        self.shuffle = shuffle
        self.playstate = True
        self.onstate = True
        self.musicprocess = False
        self.player = self.get_player()
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
            self.stop()
            raise FileNotFoundError
        self.shufflefn()


    def next(self):
        if self.counter < len(self.songs) - 1:
            self.counter+=1
        elif self.repeat:
            self.__init__(self.filename, self.shuffle, self.repeat)
        else:
            self.stop()
            raise EndOfPlaylist


    def shufflefn(self):
        if self.shuffle:
            random.shuffle(self.songs)


    def previous(self):
        if self.counter > 0:
            self.counter-=1


    def current(self):
        return self.songs[self.counter]


    def repeat_toggle(self):
        self.repeat = not self.repeat


    def repeat_state(self):
        return self.repeat

    
    def shuffle_toggle(self):
        self.shuffle = not self.shuffle
        self.shufflefn()


    def shuffle_state(self):
        return self.shuffle


    def end(self):
        self.onstate = False
        self.stop()


    def stop(self):
        self.playstate = False
        if self.musicprocess.poll() is None:
            self.musicprocess.terminate()


    def play(self):
        self.playstate = True


    def complete(self):
        if self.musicprocess.poll() is 0:
            return True
        else:
            return False
        

    def playfn(self):
        if self.player:
            command = f'{self.player} -nodisp -autoexit -hide_banner "{self.current()}"'
            self.musicprocess = subprocess.Popen(command, shell=True, bufsize=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)
            self.musicprocess.wait()


    def playing(self):
        return self.playstate


    def online(self):
        return self.onstate


    def get_player(self):
        if shutil.which("avplay"):
            return "avplay"
        elif shutil.which("ffplay"):
            return "ffplay"
        else:
            raise PlayerNotFound
            


def console():
    while True:
        control = None
        control = input()
        if control == 'skip' or control == 'next' or control == 'k' or control == 'n':
            player.stop()
            player.next()
            player.play()
        elif control == 'exit' or control == 'quit' or control == 'x' or control == 'q':
            player.end()
            shutdownfn()
        elif control == 'back' or control == 'prev' or control == 'e' or control =='b':
            player.stop()
            player.previous()
            player.play()
        elif control == 'stop' or control == 's':
            printout('Stopping.')
            player.stop()
        elif control == 'play' or control == 'p':
            player.play()
        elif control == 'help' or control == 'h' or control == '?':
            printout(HELPER2)
        elif control == 'repeat':
            player.repeat_toggle()
            printout(f'Repeat {"on" if player.repeat_state() else "off"}.')
        elif control == 'shuffle':
            player.shuffle_toggle()
            printout(f'Shuffle {"on" if player.shuffle_state() else "off"}.')


def printout(statement):
    print("\033[K\033[F\033[K", end='')
    print(f'{statement}\npycli-music>>> ', end='') 


def shutdownfn():
    print('\nExiting.')
    sys.exit(0)


def sigint_handler(signal, frame):
    shutdownfn()


signal.signal(signal.SIGINT, sigint_handler)


if __name__ == '__main__':
    shuffle = False
    repeat = False
    filename = None
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "--?" in sys.argv:
            printout(HELPER)
            sys.exit(0)
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
    player = Player(filename, shuffle, repeat)
    print(f'pycli-music: Shuffle: {"On" if shuffle else "Off"} Repeat: {"On" if repeat else "Off"}\n')
    main()