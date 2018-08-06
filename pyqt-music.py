#!/usr/bin/env python
import sys
import PyQt4
import design
import pycli_music


class MusicGUI(PyQt4.QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.player = pycli_music.Player(None, True, True)
        self.player.nonblockingLoop(self.updateSongLabel)
        self.playButton.clicked.connect(self.playPauseToggle)
        self.stopButton.clicked.connect(self.stop)
        self.nextButton.clicked.connect(self.next)
        self.previousButton.clicked.connect(self.previous)
        self.actionExit.triggered.connect(self.shutdownfn)
        self.shuffleBox.stateChanged.connect(self.player.shuffleToggle)
        self.repeatBox.stateChanged.connect(self.player.repeatToggle)
        self.updatePlayLabel("Playing")


    def next(self):
        self.player.stop()
        self.player.next()
        self.player.play()
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
        self.player.stop()
        self.player.previous()
        self.player.play()
        self.updatePlayLabel("Playing")


    def shutdownfn(self):
        self.player.end()
        sys.exit(0)


    def updateSongLabel(self):
        self.songLabel.setText(self.player.songName(self.player.currentSong()))


    def updatePlayLabel(self, string):
        self.playingLabel.setText(string)
        self.playingLabel.setFont(PyQt4.QtGui.QFont("", weight=PyQt4.QtGui.QFont.Bold))


if __name__ == '__main__':
    app = PyQt4.QtGui.QApplication(sys.argv)
    form = MusicGUI()
    form.show()
    app.exec_()
    