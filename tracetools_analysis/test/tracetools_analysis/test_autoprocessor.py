# Copyright 2019 Apex.AI, Inc.
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

from typing import Dict
from typing import Set
import unittest

from tracetools_analysis.processor import AutoProcessor
from tracetools_analysis.processor import EventHandler
from tracetools_analysis.processor import EventMetadata
from tracetools_analysis.processor import HandlerMap


class AbstractEventHandler(EventHandler):

    def __init__(self, **kwargs) -> None:
        if type(self) is AbstractEventHandler:
            raise RuntimeError()
        super().__init__(**kwargs)


class SubSubEventHandler(AbstractEventHandler):

    def __init__(self) -> None:
        handler_map: HandlerMap = {
            'myeventname': self._handler_whatever,
            'myeventname69': self._handler_whatever,
        }
        super().__init__(handler_map=handler_map)

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'myeventname',
            'myeventname69',
        }

    def _handler_whatever(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        pass


class SubSubEventHandler2(AbstractEventHandler):

    def __init__(self) -> None:
        handler_map: HandlerMap = {
            'myeventname2': self._handler_whatever,
        }
        super().__init__(handler_map=handler_map)

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'myeventname2',
        }

    def _handler_whatever(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        pass


class SubEventHandler(EventHandler):

    def __init__(self) -> None:
        handler_map: HandlerMap = {
            'myeventname3': self._handler_whatever,
        }
        super().__init__(handler_map=handler_map)

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'myeventname3',
        }

    def _handler_whatever(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        pass


class TestAutoProcessor(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def test_separate_methods(self) -> None:
        # Testing logic/methods separately, since we don't actually want to process

        # Getting subclasses
        subclasses = AutoProcessor._get_subclasses(EventHandler)
        # Will also contain the real classes
        self.assertTrue(
            all(
                handler in subclasses
                for handler in [
                    AbstractEventHandler,
                    SubSubEventHandler,
                    SubSubEventHandler2,
                    SubEventHandler,
                ]
            )
        )

        # Finding applicable classes
        event_names = {
            'myeventname',
            'myeventname2',
            'myeventname3',
        }
        applicable_handler_classes = AutoProcessor._get_applicable_event_handler_classes(
            event_names,
            subclasses,
        )
        self.assertTrue(
            all(
                handler in applicable_handler_classes
                for handler in [
                    AbstractEventHandler,
                    SubSubEventHandler2,
                    SubEventHandler,
                ]
            ) and
            SubSubEventHandler not in applicable_handler_classes
        )

        # Creating instances
        instances = AutoProcessor._get_event_handler_instances(applicable_handler_classes)
        for instance in instances:
            self.assertTrue(type(instance) is not AbstractEventHandler)

    def test_all(self) -> None:
        # Test the main method with all the logic
        events = [
            {
                '_name': 'myeventname',
                '_timestamp': 0,
                'cpu_id': 0,
            },
            {
                '_name': 'myeventname2',
                '_timestamp': 69,
                'cpu_id': 0,
            },
            {
                '_name': 'myeventname3',
                '_timestamp': 6969,
                'cpu_id': 0,
            },
        ]
        instances = AutoProcessor.get_applicable_event_handlers(events)
        for instance in instances:
            self.assertTrue(type(instance) is not AbstractEventHandler)
        # Will also contain the real classes
        self.assertEqual(
            sum(
                isinstance(instance, handler_class)
                for handler_class in [SubEventHandler, SubSubEventHandler2]
                for instance in instances
            ),
            2,
        )


if __name__ == '__main__':
    unittest.main()
