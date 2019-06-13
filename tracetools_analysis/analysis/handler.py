# Event handler

import sys

from . import lttng_models


class EventHandler():
    """Base event handling class."""

    def __init__(self, handler_map):
        """
        Constructor.

        :param handler_map (map(str: function)): the mapping from event name to handling method
        """
        self._handler_map = handler_map

    def handle_events(self, events):
        """
        Handle events by calling their handlers.

        :param events (list(dict(str:str))): the events to process
        """
        for event in events:
            self._handle(event)

    def _handle(self, event):
        event_name = lttng_models.get_name(event)
        handler_function = self._handler_map.get(event_name, None)
        if handler_function is not None:
            pid = lttng_models.get_field(event,
                                         'vpid',
                                         default=lttng_models.get_field(event,
                                                                        'pid',
                                                                        raise_if_not_found=False))
            tid = lttng_models.get_field(event,
                                         'vtid',
                                         default=lttng_models.get_field(event,
                                                                        'tid',
                                                                        raise_if_not_found=False))
            timestamp = lttng_models.get_field(event, '_timestamp')
            procname = lttng_models.get_field(event, 'procname')
            metadata = lttng_models.EventMetadata(event_name, pid, tid, timestamp, procname)
            handler_function(event, metadata)
        else:
            print(f'unhandled event name: {event_name}', file=sys.stderr)
