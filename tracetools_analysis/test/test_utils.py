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
