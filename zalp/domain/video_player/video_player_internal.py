import logging
import os
from threading import Thread, RLock

import cv2
import pyglview
from OpenGL.raw.GLUT import glutPositionWindow
from fpstimer import FPSTimer

from .events import LoadVideoEvent, PlayVideoEvent, PauseVideoEvent, StopPlayerEvent

logger = logging.getLogger(__name__)

INTRO_MOVIE = os.path.join(os.getcwd(), 'resources', 'vid_GTD19_AutomatedFrontCollisionAvoidance.mp4')

USER_MONITOR_SIZE = (2560, 1440)
CAMERA_MONITOR_SIZE = (2560, 1440)


class VideoPlayerInternal:
    def __init__(self):
        # TODO: clean-up
        self.playing = False
        self.stop_requested = False

        self.video = None

        self.window_moved = False
        self.path = ''
        self.viewer = None

        self.video_lock = None

        self.video_loopable = True

    def run(self, event_queue):
        # Lock is used to stop thread collision when reading frames and loading new movie.
        self.video_lock = RLock()

        event_handler_thread = Thread(target=self.run_event_handler, args=(event_queue,))
        event_handler_thread.start()
        self.start_player()

    def run_event_handler(self, event_queue):
        while not self.stop_requested:
            event = event_queue.get()
            self.handle_event(event)

    def start_player(self):
        self.playing = True
        self.viewer = pyglview.Viewer(
            window_width=CAMERA_MONITOR_SIZE[0],
            window_height=CAMERA_MONITOR_SIZE[1],
            borderless=True
        )
        self.load_intro_movie()

        self.viewer.set_loop(self._loop)
        self.viewer.start()  # this will block forever

    def load_intro_movie(self):
        self.load_video(INTRO_MOVIE)

    def _loop(self):
        if self.stop_requested:
            # Should kill the viewer
            return
        if self.playing:
            with self.video_lock:
                frame = self._get_next_frame()
                self.viewer.set_image(frame)

                # TODO: this moves the video only one time at player startup. If this window will be moved (e.g.
                #       monitor setup will change for a second), the window will not move back to correct spot.
                if not self.window_moved:
                    glutPositionWindow(-USER_MONITOR_SIZE[0], 0)
                    self.window_moved = True
        self.fps_timer.sleep()

    def handle_event(self, event):
        match event:
            case PlayVideoEvent():
                self.play()
            case PauseVideoEvent():
                self.pause()
            case LoadVideoEvent():
                self.load_video(event.path)
            case StopPlayerEvent():
                self.stop()
            case _:
                logger.error('VideoPlayerInternal: Unknown event')

    def load_video(self, path):
        """
        Load movie to the player.
        :param path: path to the movie. If none, intro movie will be loaded.
        """
        with self.video_lock:
            if path is None:
                self.path = INTRO_MOVIE
            else:
                self.path = path

            self._init_video()

    def _get_next_frame(self):
        ret, frame = self.video.read()
        if not ret:
            # If video is not loopable, return back current frame, do not re-init
            if not self.video_loopable:
                return self.current_frame
            # If video is loopable, re-init and get next frame again
            self._init_video()
            ret, frame = self.video.read()
            if not ret:
                logger.error('VideoPlayerInternal: Video could not be re-initialized. Playing paused')
                self.pause()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_frame = frame
        return frame

    def _init_video(self):
        # OpenCV approach
        self.video = cv2.VideoCapture(self.path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Video is only loopable if it has more than one frame
        self.video_loopable = self.frame_count > 1

        # FFMPEGCV approach - more GPU usage (but Kivy app uses it a lot too)
        # Need FFMPEG installed and added to PATH
        # self.video = ffmpegcv.VideoCapture(self.path)
        # self.fps = 30
        # self.frame_count = 181

        self.time_between_frames_ms = round((1 / self.fps) * 1000)
        self.fps_timer = FPSTimer(self.fps)

    def play(self):
        logger.info('VideoPlayerInternal: Play movie')
        self.playing = True

    def pause(self):
        logger.info('VideoPlayerInternal: Pause movie')
        self.playing = False

    def stop(self):
        # raise NotImplementedError
        # logger.info('VideoPlayerInternal: Stopping player')
        # self.playing = False
        self.stop_requested = True
        # TODO: Implement more safeguards here to make sure that every thread ended safely
        # # after all frames release the video object
        # video_player.release()
        # # close all frames form video file
        # cv2.destroyAllWindows()
        # global_allow = True
        # logger.info('VideoPlayerInternal: PLayer stopped')
        # return global_allow
