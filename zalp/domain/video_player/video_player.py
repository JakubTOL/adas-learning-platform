from multiprocessing import Process, Queue

from zalp.domain.video_player.events import PlayVideoEvent, LoadVideoEvent, StopPlayerEvent, PauseVideoEvent
from zalp.domain.video_player.video_player_internal import VideoPlayerInternal


class VideoPlayer:

    def __init__(self):
        self.event_queue = Queue()
        self.process = Process(
            target=VideoPlayerInternal().run,
            kwargs={
                'event_queue': self.event_queue
            })
        self.process.start()

    def load_video(self, path=None, play=True):
        self.event_queue.put(
            LoadVideoEvent(path)
        )
        self.play() if play else self.pause()

    def play(self):
        self.event_queue.put(PlayVideoEvent())

    def pause(self):
        self.event_queue.put(PauseVideoEvent())

    def stop(self):
        self.event_queue.put(StopPlayerEvent())
