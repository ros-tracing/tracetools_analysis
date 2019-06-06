# Process trace events and create ROS model

from .lttng_models import EventMetadata, get_field, get_name

def ros_process(events):
    """
    Process unpickled events and create ROS model
    :param events (list(dict(str:str:))): the list of events
    """
    processor = RosProcessor()
    for event in events:
        print(f'event: {str(event)}')
        processor.handle(event)

class RosProcessor():
    def __init__(self):
        # TODO add other stuff
        self.callbacks = []

        # Link a ROS trace event to its corresponding handling method
        self._handler_map = {
            'ros2:rcl_subscription_init': self._handle_subscription_init,
            'ros2:rclcpp_subscription_callback_added': self._handle_subscription_callback_added,
            'ros2:rclcpp_subscription_callback_start': self._handle_subscription_callback_start,
            'ros2:rclcpp_subscription_callback_end': self._handle_subscription_callback_end,
        }
    
    def handle(self, event):
        """
        Handle an event
        :param event (dict(str:str)): the event to handle
        """
        handler_function = self._handler_map.get(get_name(event), d=None)
        if handler_function is not None:
            name = get_name(event)
            pid = get_field(event, 'vpid', default=get_field(event, 'pid'))
            tid = get_field(event, 'vtid', default=get_field(event, 'tid'))
            timestamp = get_field(event, '_timestamp')
            procname = get_field(event, 'procname')
            metadata = EventMetadata(name, pid, tid, timestamp, procname)
            handler_function(event, metadata)

    def _handle_subscription_init(self, event, metadata):
        # TODO
        pass

    def _handle_subscription_callback_added(self, event, metadata):
        # TODO
        pass

    def _handle_subscription_callback_start(self, event, metadata):
        # TODO
        pass

    def _handle_subscription_callback_end(self, event, metadata):
        # TODO
        pass
