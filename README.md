Play all music from ~/Music by default or supply a directory or file to play.

Uses FFmpeg or avconv.

Arguments:

    '-r','--repeat' : Repeat all songs indefinitely
    '-s','--shuffle': Shuffle all songs
    '--no-console'  : Suppress console
    
Short arguments may be combined, such as '-rs'.

pycli-music console commands:

    'k', 'skip', 'n', 'next': Next song
    'e', 'prev', 'b', 'back': Previous song
    'x', 'exit', 'q', 'quit': Exit player
    's', 'stop'             : Stop song
    'p', 'play'             : Play song
    'w', 'pause'            : Pause song
    'repeat'                : Toggle repeat
    'shuffle'               : Toggle shuffle

Ctrl-c to exit.

As a library, simply construct like so for simplest usage:

    player = Player(filename=None, shuffle=False, repeat=False)
    player.blockingLoop()

Where filename is the path to the music file or directory (default is ~/Music)

Two exceptions must be handled for:

    FileNotFound
    PlayerNotFound

Where PlayerNotFound is the inability to find either FFmpeg or avconv