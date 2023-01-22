from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QIcon, QImage
import sys
import cv2
import os
import json


class VideoWindow(QMainWindow):

    def __init__(self, parent=None, moveDuration = 100):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("GUI Video Snipper Tool") 
        self.moveDuration = moveDuration
        self.video = None
        self.dirpath = None 
        self.basename = None
        self.frame_ids = {}

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setShortcut("SPACE")
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        
        self.openButton = QPushButton()
        self.openButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.openButton.clicked.connect(lambda: self.openFileFromPath(self.pathSetter.text()))
        
        self.nextButton = QPushButton()
        self.nextButton.setEnabled(False)
        self.nextButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.nextButton.clicked.connect(self.nextPosition)
        
        self.prevButton = QPushButton()
        self.prevButton.setEnabled(False)
        self.prevButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.prevButton.clicked.connect(self.prevPosition)
        
        self.savebutton = QPushButton()
        self.savebutton.setEnabled(False)
        self.savebutton.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.savebutton.clicked.connect(self.saveFrame)
        

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        
        self.angleSetter = QLineEdit()
        self.angleSetter.setEnabled(False)
        self.angleSetter.setText("0")
        
        self.pathSetter = QLineEdit()
        self.pathSetter.setText("")

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)
        
        pathLayout = QHBoxLayout()
        pathLayout.setContentsMargins(0, 0, 0, 0)
        pathLayout.addWidget(self.pathSetter)
        pathLayout.addWidget(self.openButton)

        # Create layouts to place inside widget
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)
        sliderLayout.addWidget(self.positionSlider)
        
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.prevButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.nextButton)
        controlLayout.addWidget(self.savebutton)
        controlLayout.addWidget(self.angleSetter)

        layout = QVBoxLayout()
        layout.addLayout(pathLayout)
        layout.addWidget(self.videoWidget)
        layout.addLayout(sliderLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        
    
    def openFileFromPath(self, fileName):
        if fileName != '':
            self.video = cv2.VideoCapture(fileName)
            self.basename = os.path.basename(fileName)
            self.dirpath = os.path.dirname(fileName)
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.prevButton.setEnabled(True)
            self.nextButton.setEnabled(True)
            self.savebutton.setEnabled(True)
            self.angleSetter.setEnabled(True)
            self.errorLabel.setText("")
            self.angleSetter.setText(str(0))
            self.frame_ids = {}

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())
        self.openFileFromPath(fileName)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def nextPosition(self):
        curr_position = self.mediaPlayer.position()
        self.mediaPlayer.setPosition(curr_position + self.moveDuration)

    def prevPosition(self):
        curr_position = self.mediaPlayer.position()
        self.mediaPlayer.setPosition(curr_position - self.moveDuration)

    def saveFrame(self):
        curr_position = self.mediaPlayer.position()
        fps = self.video.get(cv2.CAP_PROP_FPS)
        frame_id = int(fps * (curr_position / 1000))
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = self.video.read()
        curr_angle = int(self.angleSetter.text())
        folders = self.dirpath.split("/")[-5:]
        path = "/".join(folders)
        path = f"/Users/imdaredevil/Documents/frames/{path}"
        if not os.path.exists(path):
            os.makedirs(path)
        cv2.imwrite(f'{path}/{self.basename[:-4]}_{curr_angle}.png', frame)
        self.frame_ids[curr_angle] = frame_id
        with open(f"{path}/{self.basename[:-4]}_frame_angle.json", "w") as jsonf:
            json.dump(self.frame_ids, jsonf)
        curr_angle = (curr_angle + 45) % 360
        self.angleSetter.setText(str(curr_angle))
        
        

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.prevButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.savebutton.setEnabled(False)
        self.angleSetter.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

if __name__ == '__main__':
    moveDuration = 100
    if len(sys.argv) >= 2:
        moveDuration = int(sys.argv[1])
    app = QApplication(sys.argv)
    player = VideoWindow(moveDuration=moveDuration)
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())