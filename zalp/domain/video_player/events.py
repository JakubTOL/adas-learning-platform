from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoPlayerEvent(ABC):
    pass


@dataclass
class PlayVideoEvent(VideoPlayerEvent):
    pass


@dataclass
class PauseVideoEvent(VideoPlayerEvent):
    pass


@dataclass
class LoadVideoEvent(VideoPlayerEvent):
    path: Optional[str]


class StopPlayerEvent(VideoPlayerEvent):
    pass
