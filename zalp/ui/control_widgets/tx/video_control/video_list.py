import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode, TreeViewLabel

from zalp.application.video_list import CATALOG_LIST, DIR_PATH
from zalp.ui.control_widgets.control_widget_base import ControlWidget
from .video_control import VideoControlWidget

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'video_list.kv'))


class VideoListNode(TreeViewNode, BoxLayout):

    def __init__(self, catalog: CATALOG_LIST):
        self.catalog = catalog
        self.name = self.catalog.name
        self.subpath = self.catalog.subpath
        super().__init__()


class VideoListSubNode(TreeViewLabel):
    def __init__(self, video_file, dir_path):
        self.video_file = video_file
        self.path = os.path.join(dir_path, video_file)
        super().__init__(text=video_file)


class VideoListScrollView(ScrollView):
    tree = ObjectProperty()
    selected_node = ObjectProperty()

    def populate(self):
        for catalog in CATALOG_LIST:
            catalog_node = VideoListNode(catalog)
            self._add_catalog(catalog_node)

    def _add_catalog(self, catalog_node: VideoListNode):
        self.tree.add_node(catalog_node)
        dir_path = os.path.join(DIR_PATH, catalog_node.subpath)
        for video_file in os.listdir(dir_path):
            if True or video_file.endswith('.mp4'):  # skipping this condition
                video_file_node = VideoListSubNode(video_file, dir_path)
                self.tree.add_node(video_file_node, catalog_node)


class VideoPlayerWidget(ControlWidget, GridLayout):
    video_control_widget: VideoControlWidget = ObjectProperty()
    videolist_scroll_view: VideoListScrollView = ObjectProperty()

    def populate(self):
        self.videolist_scroll_view.populate()
        self.videolist_scroll_view.tree.bind(selected_node=self.video_control_widget.on_selected_node)
