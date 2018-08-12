#!/usr/bin/env python
from pathlib import Path
import os
import sys
import time
import json
import signal
import shutil
import random
import subprocess
import threading
import musicformat


class PlayerNotFound(Exception):
    pass


class ProberNotFound(Exception):
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
        self.songcomplete = False
        self.pausestate = False
        self.youtubedl = self.__getYoutubeDL()
        self.youtubedlcomplete = True
        self.stepper = 0
        self.volume = 100
        self.currentsongduration = None
        self.player = self.__getPlayer()
        self.prober = self.__getProber()
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


    def getPlaylist(self):
        songs = list()
        for index, song in enumerate(self.songs):
            songs.append(f'{index}: {os.path.split(song)[-1]}')
        return songs


    def sanityCheck(self, index):
        if not os.path.exists(self.songs[index]):
            self.songs[index].pop()
            return False
        else:
            return True


    def setVolume(self, level):
        self.volume = level
        self.pause()
        self.play()


    def volumeMax(self):
        self.setVolume(100)


    def volumeMute(self):
        self.setVolume(0)


    def volumeUp(self):
        if self.volume <= 90:
            self.setVolume(self.volume + 10)


    def volumeDown(self):
        if self.volume >= 10:
            self.setVolume(self.volume - 10)


    def next(self):
        if self.counter < (len(self.songs) - 1):
            self.counter += 1
        elif self.repeat:
            self.songs = self.nextsongs.copy()
            self.counter = 0
            self.nextsongs = self.loadPlaylist(self.filename)
        else:
            self.stop()
            self.counter = 0
        self.sanityCheck(self.counter)


    def skipNext(self):
        self.stop()
        self.next()
        self.play()


    def skipPrevious(self):
        self.stop()
        self.previous()
        self.play()


    def skipTo(self, index):
        if index <= len(self.songs) and self.sanityCheck(index):
            self.counter = index
            self.stop()
            self.play()
            return True
        else:
            return False



    def lastSong(self):
        if self.counter == len(self.songs):
            return True
        else:
            return False


    def firstSong(self):
        if self.counter == 0:
            return True
        else:
            return False


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
        if self.counter < (len(self.songs) - 1):
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
        self.stepper = 0
        time.sleep(0.2)
        if self.musicprocess and not self.songComplete():
            self.musicprocess.terminate()


    def play(self):
        self.playstate = True
        self.pausestate = False


    def playPauseToggle(self):
        if self.pauseState() or not self.isPlaying():
            self.play()
        else:
            self.pause()


    def pause(self):
        self.playstate = False
        self.pausestate = True
        time.sleep(0.2)
        if self.musicprocess and not self.songComplete():
            self.musicprocess.terminate()


    def pauseState(self):
        return self.pausestate


    def songComplete(self):
        return self.songcomplete


    def currentSongDuration(self):
        if not self.currentsongduration:
            probecommand = [self.prober, '-v', 'quiet', '-of', 'json', '-hide_banner', '-show_entries', 'format=duration', '-i', self.currentSong()]
            self.currentsongduration = float((json.loads(subprocess.check_output(probecommand)))['format']['duration'])
            return self.currentsongduration
        else:
            return self.currentsongduration
        

    def currentSongStep(self):
        return self.stepper


    def __play(self):
        self.songcomplete = False
        if self.player and self.prober:
            duration = self.currentSongDuration()
            timer = time.time()
            stepper = 0
            command = [self.player, '-nodisp', '-autoexit', '-hide_banner', '-ss', str(self.stepper), '-volume', str(self.volume), self.currentSong()]
            self.musicprocess = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            while self.stepper < duration and self.isPlaying():
                if time.time() >= (timer + stepper):
                    stepper += 1
                    self.stepper += 1
            self.currentsongduration = None
            if self.stepper >= duration:
                self.stepper = 0
                self.songcomplete = True
                return True
            return False
        return False


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


    def __getProber(self):
        if shutil.which("avprobe"):
            return "avprobe"
        elif shutil.which("ffplay"):
            return "ffprobe"
        else:
            raise ProberNotFound


    def __getYoutubeDL(self):
        if shutil.which("youtube-dl"):
            return True
        else:
            return False


    def currentSongName(self):
        return f'{self.counter}: {os.path.split(self.currentSong())[-1]}'


    def youtubeDL(self, link, function=None):
        if self.youtubedl and self.youtubedlcomplete == True and link:
            if function:
                youtubedlthread = threading.Thread(target=self.__youtubeDL, args=(link, function))
            else:
                youtubedlthread = threading.Thread(target=self.__youtubeDL, args=(link,))
            youtubedlthread.start()


    def __youtubeDL(self, link, function=None):
        self.youtubedlcomplete = False
        lastline = None
        command = ['youtube-dl', '-ix', '-o', f"{os.path.join(Path.home(), 'Music')}/%(uploader)s/%(title)s.%(ext)s", f'{link}']
        self.youtubedlprocess = subprocess.Popen(command, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if function:
            for line in iter(self.youtubedlprocess.stdout.readline, b''):
                if line != lastline and line != '':
                    newline = line.replace("\n", "").decode("utf-8")
                    function(f'{newline}')
                lastline = line
        self.youtubedlcomplete = True


    def nonblockingLoop(self, function=None, *args, **kwargs):
        if args or kwargs:
            self.thread = threading.Thread(target=self.blockingLoop, args=(function, args), kwargs=(kwargs))
        else:
            self.thread = threading.Thread(target=self.blockingLoop, args=(function,))
        self.thread.start()


    def blockingLoop(self, function=None, *args, **kwargs):
        try:
            while self.isOnline():
                while self.isPlaying():
                    if function:
                        if args or kwargs:
                            function(*args, **kwargs)
                        else:
                            function()
                    if self.__play():
                        self.next()
        except PlayerNotFound:
            raise PlayerNotFound
        except FileNotFoundError:
            raise FileNotFoundError
        finally:
            self.end()


if __name__ == '__main__':


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
        'u', '+', 'up'          : Volume up
        'd', '-', 'down'        : Volume down
        'M', 'max'              : Volume max
        'm', 'mute'             : Volume mute
        's', 'stop'             : Stop song
        'p', 'play'             : Play song
        'w', 'pause'            : Pause song
        'repeat'                : Toggle repeat
        'shuffle'               : Toggle shuffle
    """

    
    def console():
        while True:
            control = None
            control = input(f'\033[{height};0Hpycli-music>>> ')
            if control == 'skip' or control == 'next' or control == 'k' or control == 'n':
                player.skipNext()
            elif control == 'exit' or control == 'quit' or control == 'x' or control == 'q':
                player.end()
            elif control == 'back' or control == 'prev' or control == 'e' or control == 'b':
                player.skipPrevious()
            elif control == 'stop' or control == 's':
                player.stop()
                printout('Stopped.')
            elif control == 'play' or control == 'p':
                player.play()
                if not player.pauseState():
                    printoutCurrent()
            elif control == 'pause' or control == 'w':
                player.pause()
                printout('Paused.')
            elif control == 'help' or control == 'h' or control == '?':
                printout(HELPER2)
            elif control == 'repeat':
                player.repeatToggle()
                printout(f'Repeat {"on" if player.repeatState() else "off"}.')
            elif control == 'shuffle':
                player.shuffleToggle()
                printout(f'Shuffle {"on" if player.shuffleState() else "off"}.')
            elif control.startswith('youtube-dl'):
                player.youtubeDL(control.split()[-1], printDownload)
                printout('Downloading...')
            elif control == 'up' or control == 'u' or control == '+':
                player.volumeUp()
            elif control == 'down' or control == 'd' or control == '-':
                player.volumeDown()
            elif control == 'max' or control == 'M':
                player.volumeMax()
            elif control == 'mute' or control == 'm':
                player.volumeMute()
            time.sleep(0.1)


    def printout(statement):
        if not no_console:
            sys.stdout.write(f'\033[s\033[{height - 1};0H\033[K{statement[:width]}\033[u')
            sys.stdout.flush()
        else:
            print(f'{statement}')


    def printDownload(line):
        printout(f'youtube-dl>>> {line}')


    def printoutCurrent():
        printout(f'Playing song: {player.currentSongName()}')


    def shutdownfn():
        print('Exiting.')
        if player:
            player.end()
        sys.exit(0)


    def sigintHandler(signal, frame):
        shutdownfn()


    def sigwinchHandler(signal, frame):
        global height
        global width
        width, height = shutil.get_terminal_size()


    signal.signal(signal.SIGINT, sigintHandler)
    signal.signal(signal.SIGWINCH, sigwinchHandler)
    width, height = shutil.get_terminal_size()
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
    player.nonblockingLoop(printoutCurrent)
    time.sleep(0.1)
    thread.start()
    while player.isOnline():
        pass
    shutdownfn()