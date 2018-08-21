#!/usr/bin/env python
import sys
import PyQt5
import design
import time
import pycli_music


class MusicGUI(PyQt5.QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(PyQt5.QtWidgets.QMainWindow, self).__init__()
        self.setupUi(self)
        self.player = pycli_music.Player(None, True, True)
        self.player.nonblockingLoop()
        self.counter = 0
        self.playButton.clicked.connect(self.playPauseToggle)
        self.stopButton.clicked.connect(self.stop)
        self.nextButton.clicked.connect(self.next)
        self.previousButton.clicked.connect(self.previous)
        self.actionExit.triggered.connect(self.shutdownfn)
        self.shuffleBox.stateChanged.connect(self.shuffle)
        self.volumeSlider.sliderReleased.connect(self.setVolume)
        self.maxButton.clicked.connect(self.maxVolume)
        self.muteButton.clicked.connect(self.muteVolume)
        self.forwardButton.clicked.connect(self.player.seekForward)
        self.backButton.clicked.connect(self.player.seekBack)
        self.repeatBox.stateChanged.connect(self.player.repeatToggle)
        self.playlistWidget.itemDoubleClicked.connect(self.playlistItem)
        self.youtubedlEdit.returnPressed.connect(self.youtubedl)
        self.songlabeltimer = PyQt5.QtCore.QTimer()
        self.songlabeltimer.timeout.connect(self.updateSongLabel)
        self.songlabeltimer.start(100)
        self.updatePlayLabel("Playing")
        if not self.player.isYoutubeDLReady():
            self.youtubedlEdit.setEnabled(False)
            self.youtubedlEdit.setText('youtube-dl not found.')


    def youtubedl(self):
        self.player.youtubeDL(self.youtubedlEdit.text())
        self.youtubedlEdit.setEnabled(False)
        self.youtubedlEdit.setText('Downloading...')


    def maxVolume(self):
        self.player.volumeMax()
        self.volumeSlider.setValue(100)


    def muteVolume(self):
        self.player.volumeMute()
        self.volumeSlider.setValue(0)


    def setVolume(self):
        self.player.setVolume(self.volumeSlider.value())


    def playlistItem(self):
        if self.player.skipTo(self.playlistWidget.currentRow()):
            pass
        else:
            self.updatePlaylist()


    def updatePlaylist(self):
        self.counter = 0


    def shuffle(self):
        self.player.shuffleToggle()
        self.updatePlaylist()


    def next(self):
        self.player.skipNext()
        self.updatePlayLabel("Playing")


    def stop(self):
        self.player.stop()
        self.updatePlayLabel("Stopped")
        self.playButton.setChecked(True)


    def playPauseToggle(self):
        self.player.playPauseToggle()
        if self.player.pauseState():
            self.updatePlayLabel("Paused")
        else:
            self.updatePlayLabel("Playing")


    def previous(self):
        self.player.skipPrevious()
        self.updatePlayLabel("Playing")


    def shutdownfn(self):
        self.player.end()
        sys.exit(0)


    def updateSongLabel(self):
        self.songLabel.setText(self.player.currentlyPlaying())
        songstep = stripLeadingZeros(time.strftime("%H:%M:%S", time.gmtime(self.player.currentSongStep())))
        duration = stripLeadingZeros(time.strftime("%H:%M:%S", time.gmtime(round(self.player.currentSongDuration()))))
        timelabeltext = f'{songstep} / {duration}'
        self.timeLabel.setText(timelabeltext)
        self.progressBar.setValue((self.player.currentSongStep()/round(self.player.currentSongDuration()))*100)
        if self.player.firstSong() and self.player.currentSongStep() <= 1:
            self.updatePlaylist()
        elif self.counter < self.player.getPlaylistLength():
            if not self.playlistWidget.item(self.counter):
                self.playlistWidget.addItem(self.player.getSongAt(self.counter))
            else:
                self.playlistWidget.item(self.counter).setText(self.player.getSongAt(self.counter))
            self.counter += 1
        if self.player.isYoutubeDLReady():
            self.youtubedlEdit.setEnabled(True)
            if self.youtubedlEdit.text() == 'Downloading...':
                self.youtubedlEdit.clear()


    def updatePlayLabel(self, string):
        self.playingLabel.setText(string)
        self.playingLabel.setFont(PyQt5.QtGui.QFont("", weight=PyQt5.QtGui.QFont.Bold))


def stripLeadingZeros(string):
    strippedstring = string
    for index, char in enumerate(string):
        if char is not '0' and char is not ':' and char is not ' ':
            break
        else:
            strippedstring = string[(index + 1):]
    return strippedstring


if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    form = MusicGUI()
    form.show()
    app.exec_()
    