import os

from zalp.application.concurrency import run_in_thread
from zalp.application.video_list import DIR_PATH
from zalp.domain.video_player import VideoPlayer as VideoPlayerDomain


class VideoPlayer:
    def __init__(self):
        self._video_player = VideoPlayerDomain()

    @run_in_thread
    def load_video(self, path=None, play=True):
        """
        Load video to the player.

        :param path: relative path from the resources' path. Should only contain sub-folder and filename,
        e.g. 'Signs\\SpeedLimit30.mp4'
        If None, intro video will be played.

        :param play: True if video should be played, False otherwise
        """
        if path is not None:
            path = os.path.join(DIR_PATH, path)
        self._video_player.load_video(path, play)

    def load_default_driving_video(self):
        self.load_video('Velocity\\Driving_50kph.mp4')

    @run_in_thread
    def play(self):
        self._video_player.play()

    @run_in_thread
    def pause(self):
        self._video_player.pause()

    @run_in_thread
    def stop(self):
        self._video_player.stop()
