import datetime
import os

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView, TreeViewNode

from zalp.ui import ZalpApp

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'can.kv'))


class CanFrameTreeViewNode(TreeViewNode, BoxLayout):
    timestamp = ObjectProperty()
    data_str = ObjectProperty()

    def __init__(self, timestamp, direction, frame_id, name, data_str):
        self.timestamp = timestamp
        self.direction = direction
        self.frame_id = frame_id
        self.name = name
        self.data_str = data_str
        self.is_header = False
        super().__init__()


class CanFrameHeaderTreeViewNode(TreeViewNode, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_header = True


class CanSignalTreeViewNode(TreeViewNode, BoxLayout):
    value = ObjectProperty()
    raw_value = ObjectProperty()

    def __init__(self, name, value, raw_value):
        self.name = name
        self.value = value
        self.raw_value = raw_value
        super().__init__()


class CanTreeView(TreeView):
    def __init__(self):
        super().__init__()
        header = CanFrameHeaderTreeViewNode()
        self.add_node(header)

    def start(self, app: ZalpApp):
        app.backend.can_manager.add_callback(self.on_message)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.remove_callback(self.on_message)

    # TODO: cleanup
    @mainthread
    def on_message(self, msg):
        timestamp = datetime.datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S:%f')
        data_str = self._get_data_str(msg.data)

        # find frame, replace content if found
        for node in self.iterate_all_nodes():
            if isinstance(node, CanFrameTreeViewNode) and node.frame_id == msg.arbitration_id:
                node.timestamp = timestamp
                node.data_str = data_str
                for signal_node in node.nodes:
                    signal_node.value = msg.signals[signal_node.name]
                    signal_node.raw_value = msg.raw_signals[signal_node.name]
                return

        # unknown frame yet. add it as new node
        frame = CanFrameTreeViewNode(
            timestamp=timestamp,
            direction=msg.direction,
            frame_id=msg.arbitration_id,
            name=msg.name,
            data_str=data_str
        )

        for signal_name in msg.signals:
            signal = CanSignalTreeViewNode(name=signal_name,
                                           value=msg.signals[signal_name],
                                           raw_value=msg.raw_signals[signal_name])
            self.add_signal(signal, frame)

        self.add_frame(frame)

    def _get_data_str(self, data):
        data_list = self._pad_or_truncate(list(data), 8)
        data_list_str = [f'{n:02X}' for n in data_list]
        data_str = ' '.join(data_list_str).upper()
        return data_str

    def _pad_or_truncate(self, data_list, target_len):
        return data_list[:target_len] + [0] * (target_len - len(data_list))

    def add_frame(self, frame: CanFrameHeaderTreeViewNode):
        self.add_node(frame)

        # toggle open by default
        self.toggle_node(frame)

    def add_signal(self, signal: CanSignalTreeViewNode, frame: CanFrameHeaderTreeViewNode):
        self.add_node(signal, frame)
