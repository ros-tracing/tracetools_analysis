# Copyright 2019 Robert Bosch GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module for event handler."""

import sys
from typing import Callable
from typing import Dict
from typing import List

from tracetools_read.utils import get_event_name
from tracetools_read.utils import get_field

from .lttng_models import EventMetadata


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
        event_name = get_event_name(event)
        handler_function = self._handler_map.get(event_name, None)
        if handler_function is not None:
            pid = get_field(
                event,
                'vpid',
                default=get_field(
                    event,
                    'pid',
                    raise_if_not_found=False))
            tid = get_field(
                event,
                'vtid',
                default=get_field(
                    event,
                    'tid',
                    raise_if_not_found=False))
            timestamp = get_field(event, '_timestamp')
            procname = get_field(event, 'procname')
            metadata = EventMetadata(event_name, pid, tid, timestamp, procname)
            handler_function(event, metadata)
        else:
            print(f'unhandled event name: {event_name}', file=sys.stderr)
