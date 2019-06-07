# Process trace events and create ROS model

from .handler import EventHandler
from .lttng_models import get_field


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
    ROS-aware event processing/handling class implementation.

    Handles a trace's events and builds a model with the data.
    """

    def __init__(self):
        # Link a ROS trace event to its corresponding handling method
        handler_map = {
            'ros2:rcl_init':
                self._handle_rcl_init,
            'ros2:rcl_node_init':
                self._handle_rcl_node_init,
            'ros2:rcl_publisher_init':
                self._handle_rcl_publisher_init,
            'ros2:rcl_subscription_init':
                self._handle_subscription_init,
            'ros2:rclcpp_subscription_callback_added':
                self._handle_rclcpp_subscription_callback_added,
            'ros2:rclcpp_subscription_callback_start':
                self._handle_rclcpp_subscription_callback_start,
            'ros2:rclcpp_subscription_callback_end':
                self._handle_rclcpp_subscription_callback_end,
            'ros2:rcl_service_init':
                self._handle_rcl_service_init,
            'ros2:rclcpp_service_callback_added':
                self._handle_rclcpp_service_callback_added,
            'ros2:rclcpp_service_callback_start':
                self._handle_rclcpp_service_callback_start,
            'ros2:rclcpp_service_callback_end':
                self._handle_rclcpp_service_callback_end,
            'ros2:rcl_client_init':
                self._handle_rcl_client_init,
            'ros2:rcl_timer_init':
                self._handle_rcl_timer_init,
            'ros2:rclcpp_timer_callback_added':
                self._handle_rclcpp_timer_callback_added,
            'ros2:rclcpp_timer_callback_start':
                self._handle_rclcpp_timer_callback_start,
            'ros2:rclcpp_timer_callback_end':
                self._handle_rclcpp_timer_callback_end,
            'ros2:rclcpp_callback_register':
                self._handle_rclcpp_callback_register,
        }
        super().__init__(handler_map)

        # TODO add other stuff
        # Instances of callback_start for eventual matching
        self._callback_starts = {}
        # Callback instances, callback_address: (end - start, start)
        self.callbacks_instances = {}

    def _handle_rcl_init(self, event, metadata):
        # TODO
        pass

    def _handle_rcl_node_init(self, event, metadata):
        # TODO
        pass

    def _handle_rcl_publisher_init(self, event, metadata):
        # TODO
        pass

    def _handle_subscription_init(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_subscription_callback_added(self, event, metadata):
        # Add the callback address key and create an empty list
        callback_addr = get_field(event, 'callback')
        self.callbacks_instances[callback_addr] = []

    def _handle_rclcpp_subscription_callback_start(self, event, metadata):
        callback_addr = get_field(event, 'callback')
        self._callback_starts[callback_addr] = metadata.timestamp

    def _handle_rclcpp_subscription_callback_end(self, event, metadata):
        callback_addr = get_field(event, 'callback')
        start_timestamp = self._callback_starts.pop(callback_addr, None)
        if start_timestamp is not None:
            duration = metadata.timestamp - start_timestamp
            self.callbacks_instances[callback_addr].append((duration, start_timestamp))

    def _handle_rcl_service_init(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_service_callback_added(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_service_callback_start(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_service_callback_end(self, event, metadata):
        # TODO
        pass

    def _handle_rcl_client_init(self, event, metadata):
        # TODO
        pass

    def _handle_rcl_timer_init(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_timer_callback_added(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_timer_callback_start(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_timer_callback_end(self, event, metadata):
        # TODO
        pass

    def _handle_rclcpp_callback_register(self, event, metadata):
        # TODO
        pass
