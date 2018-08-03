#!/usr/bin/env python
from pathlib import Path
import os
import sys
import time
import signal
import shutil
import random
import subprocess
import threading
import musicformat


HELPER = """
By default, play all music from ~/Music folder, else play supplied directory or file.
>pycli-music 'argument(s)' 'path'
Arguments:
    '-r','--repeat' : Repeat all songs indefinitely
    '-s','--shuffle': Shuffle all songs
    '--no-console'  : Suppress console
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
    'w', 'pause'            : Pause song
    'repeat'                : Toggle repeat
    'shuffle'               : Toggle shuffle
"""


class PlayerNotFound(Exception):
    pass


class Player:
    def __init__(self, filename=None, shuffle=False, repeat=False):
        self.songs = list()
        self.thread = threading.Thread(target=self.blockingLoop)
        self.counter = 0
        self.repeat = repeat
        self.filename = filename
        self.shuffle = shuffle
        self.playstate = True
        self.onstate = True
        self.musicprocess = False
        self.truereturntime = 0
        self.lastpoll = 0
        self.player = self.__getPlayer()
        self.loadPlaylists()
        self.__shuffle()


    def loadPlaylist(self, filename=None):
        songs = list()
        if filename:
            music = filename
        else:
            music = os.path.join(Path.home(), 'Music')
        if os.path.isdir(music):
            for root, dirs, files in os.walk(music):
                for name in files:
                    songs.append(os.path.join(root, name))
        else:
            if os.path.isabs(music):
                songs.append(music)
            else:
                songs.append(os.path.join(os.getcwd(), music))
        for song in songs:
            try:
                form = musicformat.musicFormatHex(song)
                if form is None:
                    songs.remove(song)
            except FileNotFoundError:
                songs.remove(song)
        if len(songs) < 1:
            self.stop()
            raise FileNotFoundError
        return songs


    def loadPlaylists(self):
        self.songs = self.loadPlaylist(self.filename)
        self.nextsongs = self.loadPlaylist(self.filename)


    def next(self):
        if self.counter < len(self.songs) - 1:
            self.counter += 1
        elif self.repeat:
            self.songs = self.nextsongs.copy()
            self.nextsongs = self.loadPlaylist(self.filename)
            self.counter = 0
        else:
            self.stop()
            self.counter = 0


    def __shuffle(self):
        self.loadPlaylists()
        if self.shuffle:
            random.shuffle(self.songs)
            random.shuffle(self.nextsongs)


    def previous(self):
        if self.counter > 0:
            self.counter -= 1


    def currentSong(self):
        return self.songs[self.counter]


    def nextSong(self):
        if self.counter < len(self.songs) - 1:
            return self.songs[self.counter + 1]
        elif self.repeat:
            return self.nextsongs[0]
        else:
            return self.songs[self.counter]


    def previousSong(self):
        if self.counter > 0:
            return self.songs[self.counter - 1]
        else:
            return self.songs[self.counter]


    def repeatToggle(self):
        self.repeat = not self.repeat


    def repeatState(self):
        return self.repeat


    def shuffleToggle(self):
        self.shuffle = not self.shuffle
        self.__shuffle()


    def shuffleState(self):
        return self.shuffle


    def end(self):
        self.onstate = False
        self.stop()


    def stop(self):
        self.playstate = False
        if self.musicprocess:
            if self.musicprocess.poll() is None:
                self.musicprocess.terminate()


    def play(self):
        self.playstate = True
        self.musicprocess.send_signal(signal.SIGCONT)


    def pause(self):
        self.musicprocess.send_signal(signal.SIGSTOP)


    def songComplete(self):
        if self.musicprocess:
            if self.musicprocess.poll() is 0 and time.time() >= (self.truereturntime + 0.03):
                self.truereturntime = time.time()
                return True
            else:
                return False


    def __songComplete(self):
        if self.musicprocess:
            if self.musicprocess.poll() is 0:
                return True
            else:
                return False


    def __play(self):
        if self.player:
            command = [self.player, '-nodisp', '-autoexit', '-hide_banner', self.currentSong()]
            self.musicprocess = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.musicprocess.wait()


    def isPlaying(self):
        return self.playstate


    def isOnline(self):
        return self.onstate


    def __getPlayer(self):
        if shutil.which("avplay"):
            return "avplay"
        elif shutil.which("ffplay"):
            return "ffplay"
        else:
            raise PlayerNotFound


    def nonblockingLoop(self):
        self.thread.start()


    def blockingLoop(self):
        try:
            while self.isOnline():
                while self.isPlaying():
                    self.__play()
                    if self.__songComplete():
                        self.next()
        except PlayerNotFound:
            raise PlayerNotFound
        except FileNotFoundError:
            raise FileNotFoundError
        finally:
            self.end()


def console():
    while True:
        control = None
        control = input()
        if control == 'skip' or control == 'next' or control == 'k' or control == 'n':
            printout(f'Playing song: {player.nextSong()}')
            player.stop()
            player.next()
            player.play()
        elif control == 'exit' or control == 'quit' or control == 'x' or control == 'q':
            player.end()
        elif control == 'back' or control == 'prev' or control == 'e' or control == 'b':
            printout(f'Playing song: {player.previousSong()}')
            player.stop()
            player.previous()
            player.play()
        elif control == 'stop' or control == 's':
            printout('Stopping.')
            player.stop()
        elif control == 'play' or control == 'p':
            printout(f'Playing song: {player.currentSong()}')
            player.play()
        elif control == 'pause' or control == 'w':
            printout(f'Pausing.')
            player.pause()
        elif control == 'help' or control == 'h' or control == '?':
            printout(HELPER2)
        elif control == 'repeat':
            player.repeatToggle()
            printout(f'Repeat {"on" if player.repeatState() else "off"}.')
        elif control == 'shuffle':
            player.shuffleToggle()
            printout(f'Shuffle {"on" if player.shuffleState() else "off"}.')


def printout(statement):
    if not no_console:
        print("\033[K\033[F\033[K", end='')
        print(f'{statement}\npycli-music>>> ', end='')
    else:
        print(f'{statement}')


def shutdownfn():
    print('\nExiting.')
    if player:
        player.end()
    sys.exit(0)


def sigintHandler(signal, frame):
    shutdownfn()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigintHandler)
    no_console = False
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
                    if "--no-console" in arg:
                        no_console = True
                else:
                    if 's' in arg:
                        shuffle = True
                    if 'r' in arg:
                        repeat = True
            else:
                filename = arg
    player = Player(filename, shuffle, repeat)
    print(f'pycli-music: Shuffle: {"On" if shuffle else "Off"} Repeat: {"On" if repeat else "Off"}\n')
    if not no_console:
        thread = threading.Thread(target=console)
        thread.daemon = True
        thread.start()
    player.nonblockingLoop()
    printout(f'Playing song: {player.currentSong()}')
    while player.isOnline():
        if player.songComplete():
            printout(f'Playing song: {player.currentSong()}')
    shutdownfn()