import logging

from dotenv import load_dotenv

from zalp.application.canbus import CanManager
from zalp.application.psu import PsuService
from zalp.application.scenarios import ScenarioRunner
from zalp.application.video_player import VideoPlayer


class ZalpBase:
    """
    Main class of the application layer.
    Can be used to perform implemented every functionality without GUI.
    """

    def __init__(self):
        # load all environmental variables
        load_dotenv()

        self.set_log_level('INFO')

        self.can_manager = CanManager()
        self.psu_service = PsuService()
        self.video_player = VideoPlayer()
        self.scenario_runner = ScenarioRunner(self)

    def set_log_level(self, level):
        logging.getLogger().setLevel(level)

    def cleanup(self):
        # TODO: implement stop as kill
        # self.video_player.stop()
        self.can_manager.stop_restbus()
        self.can_manager.stop_rx_handler()

        # Do not force CAN shutdown
        # Driver should close gracefully when no app has its handle
        # self.can_manager.shutdown()

        self.psu_service.set_output(False).join()
        # TODO: crash when scenario is not running
        self.psu_service.stop()
        self.scenario_runner.cancel()
