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

from typing import Dict
import unittest

from tracetools_analysis.processor import EventHandler
from tracetools_analysis.processor import EventMetadata
from tracetools_analysis.processor import Processor


class StubHandler1(EventHandler):

    def __init__(self) -> None:
        handler_map = {
            'myeventname': self._handler_whatever,
        }
        super().__init__(handler_map=handler_map)
        self.handler_called = False

    def _handler_whatever(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        self.handler_called = True


class StubHandler2(EventHandler):

    def __init__(self) -> None:
        handler_map = {
            'myeventname': self._handler_whatever,
        }
        super().__init__(handler_map=handler_map)
        self.handler_called = False

    def _handler_whatever(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        self.handler_called = True


class WrongHandler(EventHandler):

    def __init__(self) -> None:
        handler_map = {
            'myeventname': self._handler_wrong,
        }
        super().__init__(handler_map=handler_map)

    def _handler_wrong(
        self,
    ) -> None:
        pass


class TestProcessor(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def test_handler_wrong_signature(self) -> None:
        handler = WrongHandler()
        mock_event = {
            '_name': 'myeventname',
            '_timestamp': 0,
            'cpu_id': 0,
        }
        processor = Processor(handler)
        with self.assertRaises(TypeError):
            processor.process([mock_event])

    def test_handler_method_with_merge(self) -> None:
        handler1 = StubHandler1()
        handler2 = StubHandler2()
        mock_event = {
            '_name': 'myeventname',
            '_timestamp': 0,
            'cpu_id': 0,
        }
        processor = Processor(handler1, handler2)
        processor.process([mock_event])
        self.assertTrue(handler1.handler_called, 'event handler not called')
        self.assertTrue(handler2.handler_called, 'event handler not called')


if __name__ == '__main__':
    unittest.main()
