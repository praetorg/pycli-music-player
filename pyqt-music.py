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
        self.playButton.clicked.connect(self.player.playPauseToggle)
        self.stopButton.clicked.connect(self.player.stop)
        self.nextButton.clicked.connect(self.next)
        self.previousButton.clicked.connect(self.previous)
        self.actionExit.triggered.connect(self.shutdownfn)
        self.shuffleBox.stateChanged.connect(self.player.shuffleToggle)
        self.repeatBox.stateChanged.connect(self.player.repeatToggle)


    def next(self):
        self.player.stop()
        self.player.next()
        self.player.play()


    def previous(self):
        self.player.stop()
        self.player.previous()
        self.player.play()


    def shutdownfn(self):
        self.player.end()
        sys.exit(0)


    def updateSongLabel(self):
        self.songLabel.setText(self.player.songName(self.player.currentSong()))


if __name__ == '__main__':
    app = PyQt4.QtGui.QApplication(sys.argv)
    form = MusicGUI()
    form.show()
    app.exec_()
    