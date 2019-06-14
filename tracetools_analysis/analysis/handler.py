# Event handler

import sys
from typing import Callable
from typing import Dict
from typing import List

from .lttng_models import EventMetadata
from .lttng_models import get_field
from .lttng_models import get_name


class EventHandler():
    """Base event handling class."""

    def __init__(self, handler_map: Dict[str, Callable[[Dict, EventMetadata], None]]) -> None:
        """
        Constructor.

        :param handler_map: the mapping from event name to handling method
        """
        self._handler_map = handler_map

    def handle_events(self, events: List[Dict[str, str]]) -> None:
        """
        Handle events by calling their handlers.

        :param events: the events to process
        """
        for event in events:
            self._handle(event)

    def _handle(self, event: Dict[str, str]) -> None:
        event_name = get_name(event)
        handler_function = self._handler_map.get(event_name, None)
        if handler_function is not None:
            pid = get_field(event,
                            'vpid',
                            default=get_field(event,
                                              'pid',
                                              raise_if_not_found=False))
            tid = get_field(event,
                            'vtid',
                            default=get_field(event,
                                              'tid',
                                              raise_if_not_found=False))
            timestamp = get_field(event, '_timestamp')
            procname = get_field(event, 'procname')
            metadata = EventMetadata(event_name, pid, tid, timestamp, procname)
            handler_function(event, metadata)
        else:
            print(f'unhandled event name: {event_name}', file=sys.stderr)
