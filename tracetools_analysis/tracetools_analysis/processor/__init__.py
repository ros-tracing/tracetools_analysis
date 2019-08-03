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
from typing import Set
from typing import Type

from tracetools_read import DictEvent
from tracetools_read import get_event_name
from tracetools_read import get_field


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

    def __init__(
        self,
        *,
        handler_map: HandlerMap,
        **kwargs,
    ) -> None:
        """
        Constructor.

        :param handler_map: the mapping from event name to handling method
        """
        print(f'{self.__class__.__name__}.**kwargs={kwargs}')
        assert handler_map is not None and len(handler_map) > 0, f'empty map: {handler_map}'
        self._handler_map = handler_map
        self.processor = None

    @property
    def handler_map(self) -> HandlerMap:
        """Get the handler functions map."""
        return self._handler_map

    @staticmethod
    def dependencies() -> List[Type['EventHandler']]:
        """
        Get the `EventHandler`s that should also exist along with this current one.

        Subclasses should override this method id they want to declare dependencies
        Default: no dependencies.
        """
        return []

    def register_processor(self, processor: 'Processor') -> None:
        """Register processor with this `EventHandler` so that it can query other handlers."""
        self.processor = processor

    @classmethod
    def process(cls, events: List[DictEvent], **kwargs) -> 'EventHandler':
        """
        Create a `Processor` and process an instance of the class.

        :param events: the list of events
        :return: the processor object after processing
        """
        assert cls != EventHandler, 'only call process() from inheriting classes'
        handler_object = cls(**kwargs)  # pylint: disable=all
        processor = Processor(handler_object, **kwargs)
        processor.process(events)
        return handler_object


class DepedencySolver():
    """
    Solve `EventHandler` dependencies.

    Post-order depth-first search (ish).
    """

    @staticmethod
    def solve(initial_handlers: List[EventHandler]) -> List[EventHandler]:
        """
        Solve.

        :param initial_handlers: the initial handlers for which to check dependencies, in order
        :return: the solved list, in order
        """
        visited: Set[Type[EventHandler]] = set()
        result: List[EventHandler] = []
        for handler in initial_handlers:
            DepedencySolver._solve_instance(handler, visited, result)
        return result

    def _solve_instance(
        handler_instance: EventHandler,
        visited: Set[Type[EventHandler]],
        result: List[EventHandler],
    ) -> None:
        if type(handler_instance) not in visited:
            for dependency_type in type(handler_instance).dependencies():
                DepedencySolver._solve_type(dependency_type, visited, result)
            visited.add(type(handler_instance))
            result.append(handler_instance)

    @staticmethod
    def _solve_type(
        handler_type: Type[EventHandler],
        visited: Set[Type[EventHandler]],
        result: List[EventHandler],
    ) -> None:
        if handler_type not in visited:
            for dependency_type in handler_type.dependencies():
                DepedencySolver._solve_type(dependency_type, visited, result)
            visited.add(handler_type)
            # FIXME if it exists in the initial handler instances use that instead
            # otherwise that instance is going to be replaced by the new instance below
            result.append(handler_type())


class Processor():
    """Base processor class."""

    def __init__(
        self,
        *handlers: EventHandler,
        **kwargs,
    ) -> None:
        """
        Constructor.

        :param handlers: the `EventHandler`s to use for processing
        """
        self._handlers = list(handlers)
        print('handlers before:', [type(handler).__name__ for handler in self._handlers])
        self._handlers = self._expand_dependencies(self._handlers, **kwargs)
        print('handlers after:', [type(handler).__name__ for handler in self._handlers])
        self._register_with_handlers()
        input()

    def _register_with_handlers(self) -> None:
        """Register this processor with its `EventHandler`s."""
        for handler in self._handlers:
            handler.register_processor(self)

    def _expand_dependencies(
        self,
        handlers: List[EventHandler],
        **kwargs,
    ) -> List[EventHandler]:
        """
        Check handlers and add dependencies if not included.

        :param handlers: the list of primary `EventHandler`s
        """
        # TODO pass on **kwargs
        return DepedencySolver.solve(handlers)

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
