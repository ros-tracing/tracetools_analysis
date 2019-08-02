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

"""Base processor module."""

from collections import defaultdict
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from tracetools_read.utils import DictEvent
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


HandlerMap = Dict[str, Callable[[DictEvent, EventMetadata], None]]
HandlerMultimap = Dict[str, List[Callable[[DictEvent, EventMetadata], None]]]


class EventHandler():
    """
    Base event handling class.

    Provides handling functions for some events, depending on the name.
    """

    def __init__(self, handler_map: HandlerMap) -> None:
        """
        Constructor.

        :param handler_map: the mapping from event name to handling method
        """
        assert handler_map is not None and len(handler_map) > 0, f'empty map: {handler_map}'
        self._handler_map = handler_map

    @property
    def handler_map(self) -> HandlerMap:
        """Get the handler functions map."""
        return self._handler_map

    @property
    def dependencies(self) -> List[Type['EventHandler']]:
        """
        Get the `EventHandler`s that should also exist along with this current one.

        Subclasses should override this method id they want to declare dependencies
        Default: no dependencies.
        """
        return []

    @classmethod
    def process(cls, events: List[DictEvent]) -> 'EventHandler':
        """
        Create a `Processor` and process an instance of the class.

        :param events: the list of events
        :return: the processor object after processing
        """
        assert cls != EventHandler, 'only call process() from inheriting classes'
        handler_object = cls()  # pylint: disable=no-value-for-parameter
        processor = Processor(handler_object)
        processor.process(events)
        return handler_object


class Processor():
    """Base processor class."""

    def __init__(self, *handlers: EventHandler) -> None:
        """
        Constructor.

        :param handlers: the `EventHandler`s to use for processing
        """
        self._handlers = list(handlers)
        print('handlers before:', [type(handler).__name__ for handler in self._handlers])
        self._add_dependant_handlers(self._handlers)
        print('handlers after:', [type(handler).__name__ for handler in self._handlers])
        self._register(self._handlers)

    def _add_dependant_handlers(self, handlers: List[EventHandler]) -> None:
        """
        Check handlers and add dependant handlers if not included. Ordered.

        :param handlers: the list of primary `EventHandler`s
        """
        # TODO
        # For each handler object, check if its dependencies are included
        # If not, add them _before_
        pass

    def _get_handler_maps(self) -> HandlerMultimap:
        """
        Collect and merge `HandlerMap`s from all events handlers into a `HandlerMultimap`.

        :return: the merged multimap
        """
        handler_multimap = defaultdict(list)
        for handler in self._handlers:
            handler_map = handler.handler_map
            print(f'{handler}:: {handler_map}')
            for event_name, handler in handler_map.items():
                handler_multimap[event_name].append(handler)
        return handler_multimap

    def process(self, events: List[DictEvent]) -> None:
        """
        Process all events.

        :param events: the events to process
        """
        self._handler_multimap = self._get_handler_maps()
        print(f'multimap: {self._handler_multimap}')
        for event in events:
            self._process_event(event)

    def _process_event(self, event: DictEvent) -> None:
        """Process a single event."""
        event_name = get_event_name(event)
        print(f"event name: {event_name}")
        handler_functions = self._handler_multimap.get(event_name, None)
        if handler_functions is not None:
            print(f'\thandler functions: {handler_functions}')
            for handler_function in handler_functions:
                print(f'\t\thandler function: {handler_function}')
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
                input()
