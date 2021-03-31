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

from typing import Any
from typing import Dict
from typing import List
import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.profile import ProfileHandler
from tracetools_read import DictEvent


# TEST DATA
#
# + Threads:
#       0: does whatever
#       1: contains one instance of the functions of interest
#       2: contains another instance of the functions of interest
#
# + Functions structure
#       function_a
#           function_aa
#       function_b
#
# + Timeline
#                                              tid  1              2
#                                             func     a  aa   b     a  aa   b
#                                             time
#       0   : whatever
#       3   : sched_switch from tid 0 to tid 1
#       5   : tid 1, func_entry: function_a
#       7   : sched_switch from tid 1 to tid 0         2
#       10  : sched_switch from tid 0 to tid 2
#       11  : tid 2, func_entry: function_a
#       15  : sched_switch from tid 2 to tid 1                       4
#       16  : tid 1, func_entry: function_aa           1
#       20  : sched_switch from tid 1 to tid 2         4   4
#       27  : tid 2, func_entry: function_aa                         7
#       29  : sched_switch from tid 2 to tid 1                       2   2
#       30  : tid 1, func_exit: (function_aa)          1   1
#       32  : sched_switch from tid 1 to tid 0         2
#       34  : sched_switch from tid 0 to tid 2
#       35  : tid 2, func_exit: (function_aa)                        1   1
#       37  : tid 2, func_exit: (function_a)                         2
#       39  : tid 2, func_entry: function_b
#       40  : tid 2, func_exit: (function_b)                                 1
#       41  : sched_switch from tid 2 to tid 1
#       42  : tid 1, func_exit: (function_a)           1
#       44  : tid 1, func_entry: function_b
#       47  : sched_switch from tid 1 to tid 0                 3
#       49  : sched_switch from tid 0 to tid 1
#       60  : tid 1, func_exit: (function_b)                  11
#       69  : sched_switch from tid 1 to tid 0
#
#                                            total    11   5  14    16   3   1


input_events = [
    {
        '_name': 'sched_switch',
        '_timestamp': 3,
        'prev_tid': 0,
        'next_tid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 5,
        'vtid': 1,
        'addr': '0xfA',
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 7,
        'prev_tid': 1,
        'next_tid': 0,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 10,
        'prev_tid': 0,
        'next_tid': 2,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 11,
        'vtid': 2,
        'addr': '0xfA',
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 15,
        'prev_tid': 2,
        'next_tid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 16,
        'vtid': 1,
        'addr': '0xfAA',
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 20,
        'prev_tid': 1,
        'next_tid': 2,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 27,
        'vtid': 2,
        'addr': '0xfAA',
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 29,
        'prev_tid': 2,
        'next_tid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 30,
        'vtid': 1,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 32,
        'prev_tid': 1,
        'next_tid': 0,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 34,
        'prev_tid': 0,
        'next_tid': 2,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 35,
        'vtid': 2,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 37,
        'vtid': 2,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 39,
        'vtid': 2,
        'addr': '0xfB',
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 40,
        'vtid': 2,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 41,
        'prev_tid': 2,
        'next_tid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 42,
        'vtid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_entry',
        '_timestamp': 44,
        'vtid': 1,
        'addr': '0xfB',
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 47,
        'prev_tid': 1,
        'next_tid': 0,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 49,
        'prev_tid': 0,
        'next_tid': 1,
    },
    {
        '_name': 'lttng_ust_cyg_profile_fast:func_exit',
        '_timestamp': 60,
        'vtid': 1,
    },
    {
        '_name': 'sched_switch',
        '_timestamp': 69,
        'prev_tid': 1,
        'next_tid': 0,
    },
]


expected = [
    {
        'tid': 1,
        'depth': 1,
        'function_name': '0xfAA',
        'parent_name': '0xfA',
        'start_timestamp': 16,
        'duration': 14,
        'actual_duration': 5,
    },
    {
        'tid': 2,
        'depth': 1,
        'function_name': '0xfAA',
        'parent_name': '0xfA',
        'start_timestamp': 27,
        'duration': 8,
        'actual_duration': 3,
    },
    {
        'tid': 2,
        'depth': 0,
        'function_name': '0xfA',
        'parent_name': None,
        'start_timestamp': 11,
        'duration': 26,
        'actual_duration': 16,
    },
    {
        'tid': 2,
        'depth': 0,
        'function_name': '0xfB',
        'parent_name': None,
        'start_timestamp': 39,
        'duration': 1,
        'actual_duration': 1,
    },
    {
        'tid': 1,
        'depth': 0,
        'function_name': '0xfA',
        'parent_name': None,
        'start_timestamp': 5,
        'duration': 37,
        'actual_duration': 11,
    },
    {
        'tid': 1,
        'depth': 0,
        'function_name': '0xfB',
        'parent_name': None,
        'start_timestamp': 44,
        'duration': 16,
        'actual_duration': 14,
    },
]


address_to_func = {
    '0xfA': '0xfA',
    '0xfAA': '0xfAA',
    '0xfB': '0xfB',
}


class TestProfileHandler(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    @staticmethod
    def build_expected_df(expected_data: List[Dict[str, Any]]) -> DataFrame:
        # Columns should be in the same order
        return DataFrame.from_dict(expected_data)

    @staticmethod
    def transform_fake_fields(events: List[DictEvent]) -> None:
        for event in events:
            # Actual value does not matter here; it just needs to be there
            event['cpu_id'] = 69
            if event['_name'] == 'lttng_ust_cyg_profile_fast:func_entry':
                # The 'addr' field is supposed to be an int
                event['addr'] = ProfileHandler.addr_to_int(event['addr'])

    @classmethod
    def setUpClass(cls):
        cls.transform_fake_fields(input_events)
        cls.expected = cls.build_expected_df(expected)
        cls.handler = ProfileHandler(address_to_func=address_to_func)
        cls.processor = Processor(cls.handler)
        cls.processor.process(input_events)

    def test_profiling(self) -> None:
        handler = self.__class__.handler  # type: ignore
        expected_df = self.__class__.expected  # type: ignore
        result_df = handler.data.times
        assert_frame_equal(result_df, expected_df)


if __name__ == '__main__':
    unittest.main()
