import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from solution.HandDetectionModule import get_sign
import cv2
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("GESTURE RECOGNITION VIDEO PLAYER")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.resize(1600, 900)
        self.setStyleSheet("background-color: #22223b")
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.menu = QMenuBar()
        self.menu.addMenu("MENU")
        self.menu.addMenu("INSTRUCTIONS")
        self.menu.addMenu("ABOUT")
        self.menu.setWindowTitle("Gesture recognition video player")
        self.menu.setStyleSheet(
            "background-color: #c9ada7; color: #22223b; font-weight: bold; font-size: 15; align-items: stretch;")
        self.setMenuBar(self.menu)

        self.horizontal_box = QHBoxLayout()
        self.vertical_box1 = QVBoxLayout()
        self.vertical_box2 = QVBoxLayout()

        self.horizontal_box.setContentsMargins(5, 5, 5, 5)
        self.horizontal_box.setSpacing(5)

        self.camera_feed = QLabel()
        self.camera_feed.setStyleSheet(
            "background-color: gray; border-style: solid; border-color: gray; border-width: 1px;")
        self.vertical_box1.addWidget(self.camera_feed)

        self.camera = Camera()
        self.camera.start()
        self.camera.image_update.connect(self.ImageUpdateSlot)
        self.camera.gesture_action.connect(self.ActionsOnVideo)

        self.cancel_button = QPushButton("")
        self.cancel_button.setText("CANCEL")
        self.cancel_button.clicked.connect(self.CancelFeed)
        self.cancel_button.setFixedWidth(640)
        self.cancel_button.setStyleSheet(
            '''*{
            padding: 15px 0px;
            background: '#4a4e69';
            color: #ff1b9e;
            font-weight: bold;
            font-family: 'Shanti';
            font-size: 25px;
            border-radius: 30px;
            margin: 5px 150px;
            }
                *:hover{
                background: '#ff1b9e';
                color: #99D5C9;
        }''')

        self.vertical_box1.addWidget(self.cancel_button)

        label = QLabel(self)
        pixmap = QPixmap('image.jpg').scaled(640, 300, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        self.vertical_box1.addWidget(label)

        self.video_player = VideoPlayer()
        self.vertical_box2.addWidget(self.video_player)

        self.horizontal_box.addLayout(self.vertical_box1)
        self.horizontal_box.addLayout(self.vertical_box2)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.horizontal_box)
        self.setCentralWidget(self.main_widget)

    def ImageUpdateSlot(self, image):
        self.camera_feed.setPixmap(QPixmap.fromImage(image))

    def CancelFeed(self):
        self.camera.stop()
        sys.exit(app.exec_())

    def ActionsOnVideo(self, info: str):
        if info == 'PAUSE':
            self.video_player.media_player.pause()
        elif info == 'PLAY':
            self.video_player.media_player.play()
        elif info.startswith('VOLUME') and not info.endswith('CONTROL'):
            self.video_player.media_player.setVolume(int(info[-1]))
        elif info == 'FF':
            self.video_player.media_player.setPosition(self.video_player.media_player.position() + 10000)
        elif info == 'REWIND':
            self.video_player.media_player.setPosition(self.video_player.media_player.position() - 10000)
        elif info == 'PREV':
            self.video_player.previous_video_change()
        elif info == 'NEXT':
            self.video_player.next_video_change()
        elif info == 'MUTE':
            self.video_player.media_player.setVolume(0)


class Camera(QThread):
    active_thread: bool
    image_update = pyqtSignal(QImage)
    gesture_action = pyqtSignal(str)
    video_capture = cv2.VideoCapture(0)

    def run(self):
        self.active_thread = True
        video_capture = cv2.VideoCapture(0)

        on_screen_command = ''
        action = ''
        command_counter = 0
        while self.active_thread:
            ret, image = video_capture.read()
            h, w, c = image.shape
            if ret:

                action = get_sign(image, True)

                self.gesture_action.emit(action)

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                if not action in ['NOT RECOGNIZED', '', 'Do a fist', 'Swipe']:
                    if not action.__eq__(on_screen_command):
                        command_counter = 0
                        on_screen_command = action

                if not on_screen_command.__eq__('') and command_counter < 20:
                    cv2.putText(image, on_screen_command, (10, h - 50), cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                    command_counter += 1

                convert_to_qt_format = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
                pic = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)


                self.image_update.emit(pic)

    def stop(self):
        self.active_thread = False
        self.quit()


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        self.resize(200, 200)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.video_widget = QVideoWidget()

        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)

        # new code ------
        self.forward_button = QPushButton()
        self.forward_button.setEnabled(True)
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        # self.forward_button.clicked.connect(self.ff_rewind)
        # ---------------

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.error = QLabel()
        self.error.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        open_button = QPushButton("Open Video")
        open_button.setToolTip("Open Video File")
        open_button.setStatusTip("Open Video File")
        # open_button.setFixedHeight(24)
        open_button.setStyleSheet(
            '''*{
            padding: 15px 0px;
            background: '#4a4e69';
            color: #ff1b9e;
            font-weight: bold;
            font-family: 'Shanti';
            font-size: 25px;
            border-radius: 30px;
            margin: 5px 150px;
            }
                *:hover{
                background: '#ff1b9e';
                color: #99D5C9;
        }''')
        open_button.clicked.connect(self.openFile)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.forward_button)
        control_layout.addWidget(self.position_slider)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        layout.addWidget(self.error)
        layout.addWidget(open_button)

        self.setLayout(layout)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_error)

    videos = ["D:/Python_Projects/HandDetection/videos/1.wmv",
              "D:/Python_Projects/HandDetection/videos/2.wmv",
              "D:/Python_Projects/HandDetection/videos/3.wmv",
              "D:/Python_Projects/HandDetection/videos/4.wmv",
              "D:/Python_Projects/HandDetection/videos/5.wmv",
              "D:/Python_Projects/HandDetection/videos/6.wmv",
              "D:/Python_Projects/HandDetection/videos/7.wmv"]
    opened_video = ""

    def index_of_video(self):
        for i in range(len(self.videos)):
            if self.opened_video == self.videos[i]:
                return i

    def previous_video_change(self):
        if self.opened_video != '':
            index = self.index_of_video()
            if index == 0:
                return
            else:
                self.opened_video = self.videos[index - 1]
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.opened_video)))
            self.play_button.setEnabled(True)

    def next_video_change(self):
        if self.opened_video != '':
            index = self.index_of_video()
            if index == 6:
                return
            else:
                self.opened_video = self.videos[index + 1]
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.opened_video)))
            self.play_button.setEnabled(True)

    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())

        if file_name!='':
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(file_name)))
            self.opened_video = file_name
            self.play_button.setEnabled(True)
        index, = np.where(self.videos == self.opened_video)
        print(index)

    def play_video(self):
        if self.media_player.state()==QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.state()==QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_error(self):
        self.play_button.setEnabled(False)
        self.error.setText("Error: " + self.media_player.errorString())


if __name__=='__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
