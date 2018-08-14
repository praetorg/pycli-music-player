#!/usr/bin/env python
import sys
import PyQt4
import design
import time
import pycli_music


class MusicGUI(PyQt4.QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(PyQt4.QtGui.QMainWindow, self).__init__()
        self.setupUi(self)
        self.player = pycli_music.Player(None, True, True)
        self.player.nonblockingLoop()
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
        self.songlabeltimer = PyQt4.QtCore.QTimer()
        self.songlabeltimer.timeout.connect(self.updateSongLabel)
        self.songlabeltimer.start(500)
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
            self.updatePlaylistWidget()


    def updatePlaylistWidget(self):
        self.playlistWidget.clear()
        self.playlistWidget.addItems(self.player.getPlaylist())


    def shuffle(self):
        self.player.shuffleToggle()
        self.updatePlaylistWidget()


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
        self.songLabel.setText(self.player.currentSongName())
        songstep = time.strftime("%H:%M:%S", time.gmtime(self.player.currentSongStep()))
        duration = time.strftime("%H:%M:%S", time.gmtime(round(self.player.currentSongDuration())))
        self.timeLabel.setText(f'{songstep}/{duration}'.replace("00:", ""))
        self.progressBar.setValue((self.player.currentSongStep()/round(self.player.currentSongDuration()))*100)
        if self.player.firstSong():
            self.updatePlaylistWidget()
        if self.player.isYoutubeDLReady():
            self.youtubedlEdit.setEnabled(True)


    def updatePlayLabel(self, string):
        self.playingLabel.setText(string)
        self.playingLabel.setFont(PyQt4.QtGui.QFont("", weight=PyQt4.QtGui.QFont.Bold))


if __name__ == '__main__':
    app = PyQt4.QtGui.QApplication(sys.argv)
    form = MusicGUI()
    form.show()
    app.exec_()
    