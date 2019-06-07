# Process trace events and create ROS model

import sys
from .lttng_models import get_field
from .handler import EventHandler

def ros_process(events):
    """
    Process unpickled events and create ROS model.

    :param events (list(dict(str:str:))): the list of events
    :return the processor object
    """
    processor = RosProcessor()
    processor.process_events(events)
    return processor


class RosProcessor(EventHandler):
    """
    ROS-aware event processing/handling class.

    Handles a trace's events and builds a model with the data.
    """

    def __init__(self):
        # TODO add other stuff
        # Instances of callback_start for eventual matching
        self._callback_starts = {}
        # Callback instances, callback_address: (end - start, start)
        self.callbacks_instances = {}

        # Link a ROS trace event to its corresponding handling method
        self._handler_map = {
            'ros2:rcl_subscription_init': self._handle_subscription_init,
            'ros2:rclcpp_subscription_callback_added': self._handle_subscription_callback_added,
            'ros2:rclcpp_subscription_callback_start': self._handle_subscription_callback_start,
            'ros2:rclcpp_subscription_callback_end': self._handle_subscription_callback_end,
        }

    def _handle_subscription_init(self, event, metadata):
        # TODO
        pass

    def _handle_subscription_callback_added(self, event, metadata):
        # Add the callback address key and create an empty list
        callback_addr = get_field(event, 'callback')
        self.callbacks_instances[callback_addr] = []

    def _handle_subscription_callback_start(self, event, metadata):
        callback_addr = get_field(event, 'callback')
        self._callback_starts[callback_addr] = metadata.timestamp

    def _handle_subscription_callback_end(self, event, metadata):
        callback_addr = get_field(event, 'callback')
        start_timestamp = self._callback_starts.pop(callback_addr, None)
        if start_timestamp is not None:
            duration = metadata.timestamp - start_timestamp
            self.callbacks_instances[callback_addr].append((duration, start_timestamp))
