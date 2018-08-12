# pycli-music-player

Play all music from ~/Music by default or supply a directory or file to play.

Uses FFmpeg or avconv.

## Arguments:

    '-r','--repeat' : Repeat all songs indefinitely
    '-s','--shuffle': Shuffle all songs
    '--no-console'  : Suppress console
    
Short arguments may be combined, such as `-rs`.

## Console Commands:

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

## Library/Module Use

As a library, simply construct like so for simplest usage:

    player = Player(filename=None, shuffle=False, repeat=False)
    player.blockingLoop(function=None)

Where `filename` is the path to the music file or directory (default is ~/Music)
and `function` is a function to pass through to the loop to be executed every song change(including immediately).

Three exceptions must be handled for:

    FileNotFound
    PlayerNotFound
    ProberNotFound

Where PlayerNotFound is the inability to find either FFplay or avplay, and ProberNotFound is the inability to find
either FFprobe or avprobe.