#!/usr/bin/env python3
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

import unittest

from tracetools_analysis import time_diff_to_str
from tracetools_analysis.data_model.ros2 import Ros2DataModel
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil


class TestUtils(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def test_time_diff_to_str(self) -> None:
        self.assertEqual('11 ms', time_diff_to_str(0.0106))
        self.assertEqual('6.9 s', time_diff_to_str(6.9069))
        self.assertEqual('1 m 10 s', time_diff_to_str(69.6969))
        self.assertEqual('6 m 10 s', time_diff_to_str(369.6969))
        self.assertEqual('2 m 0 s', time_diff_to_str(120.499999999))

    def test_ros2_no_callbacks(self) -> None:
        data_model = Ros2DataModel()
        data_model.finalize()
        util = Ros2DataModelUtil(data_model)
        self.assertEqual({}, util.get_callback_symbols())
