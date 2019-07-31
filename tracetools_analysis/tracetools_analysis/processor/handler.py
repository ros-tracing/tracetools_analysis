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

"""Module for event handling."""

from typing import Callable
from typing import Dict
from typing import List

from tracetools_read.utils import get_event_name
from tracetools_read.utils import get_field


class EventMetadata():
    """Container for event metadata."""

    def __init__(
        self,
        event_name: str,
        timestamp: int,
        cpu_id: int,
        procname: str = None,
        pid: int = None,
        tid: int = None,
    ) -> None:
        """
        Constructor.

        Parameters with a default value of `None` are not mandatory,
        since they are not always present.
        """
        self._event_name = event_name
        self._timestamp = timestamp
        self._cpu_id = cpu_id
        self._procname = procname
        self._pid = pid
        self._tid = tid

    @property
    def event_name(self):
        return self._event_name

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def cpu_id(self):
        return self._cpu_id

    @property
    def procname(self):
        return self._procname

    @property
    def pid(self):
        return self._pid

    @property
    def tid(self):
        return self._tid


class EventHandler():
    """Base event handling class."""

    def __init__(self, handler_map: Dict[str, Callable[[Dict, EventMetadata], None]]) -> None:
        """
        Constructor.

        :param handler_map: the mapping from event name to handling method
        """
        assert handler_map is not None and len(handler_map) > 0, f'empty map: {handler_map}'
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
            timestamp = get_field(event, '_timestamp')
            cpu_id = get_field(event, 'cpu_id')
            # TODO perhaps validate fields depending on the type of event,
            # i.e. all UST events should have procname, (v)pid and (v)tid
            # context info, since analyses might not work otherwise
            procname = get_field(event, 'procname', raise_if_not_found=False)
            pid = get_field(
                event,
                'vpid',
                default=get_field(
                    event,
                    'pid',
                    raise_if_not_found=False),
                raise_if_not_found=False)
            tid = get_field(
                event,
                'vtid',
                default=get_field(
                    event,
                    'tid',
                    raise_if_not_found=False),
                raise_if_not_found=False)
            metadata = EventMetadata(event_name, timestamp, cpu_id, procname, pid, tid)
            handler_function(event, metadata)

    @classmethod
    def process(cls, events: List[Dict[str, str]]) -> 'EventHandler':
        """
        Create processor and process unpickled events to create model.

        :param events: the list of events
        :return: the processor object after processing
        """
        assert cls != EventHandler, 'only call process() from inheriting classes'
        processor = cls()  # pylint: disable=no-value-for-parameter
        processor.handle_events(events)
        return processor
