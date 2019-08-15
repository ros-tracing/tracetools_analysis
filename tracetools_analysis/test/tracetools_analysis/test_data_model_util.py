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

from datetime import datetime
from datetime import timezone
import unittest

from pandas import DataFrame
from pandas.util.testing import assert_frame_equal

from tracetools_analysis.utils import DataModelUtil


class TestDataModelUtil(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def test_convert_time_columns(self) -> None:
        input_df = DataFrame(
            data=[
                {
                    'timestamp': 1565177400000*1000000,
                    'random_thingy': 'abc',
                    'some_duration': 3000000,
                    'const_number': 123456,
                },
                {
                    'timestamp': 946684800000*1000000,
                    'random_thingy': 'def',
                    'some_duration': 10000000,
                    'const_number': 789101112,
                },
            ],
        )
        expected_df = DataFrame(
            data=[
                {
                    'timestamp': datetime(2019, 8, 7, 11, 30, 0, tzinfo=timezone.utc),
                    'random_thingy': 'abc',
                    'some_duration': 3,
                    'const_number': 123456,
                },
                {
                    'timestamp': datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    'random_thingy': 'def',
                    'some_duration': 10,
                    'const_number': 789101112,
                },
            ],
        )
        result_df = DataModelUtil.convert_time_columns(
            input_df,
            ['some_duration'],
            ['timestamp'],
            inplace=True,
        )
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_compute_column_difference(self) -> None:
        input_df = DataFrame(
            data=[
                {
                    'a': 10,
                    'b': 13,
                    'c': 1,
                },
                {
                    'a': 1,
                    'b': 3,
                    'c': 69,
                },
            ],
        )
        expected_df = DataFrame(
            data=[
                {
                    'a': 10,
                    'b': 13,
                    'c': 1,
                    'diff': 3,
                },
                {
                    'a': 1,
                    'b': 3,
                    'c': 69,
                    'diff': 2,
                },
            ],
        )
        DataModelUtil.compute_column_difference(
            input_df,
            'b',
            'a',
            'diff',
        )
        assert_frame_equal(input_df, expected_df)


if __name__ == '__main__':
    unittest.main()
