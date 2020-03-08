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

import unittest

from tracetools_analysis.processor import Dependant
from tracetools_analysis.processor import DependencySolver


class DepEmtpy(Dependant):

    def __init__(self, **kwargs) -> None:
        self.myparam = kwargs.get('myparam', None)


class DepOne(Dependant):

    @staticmethod
    def dependencies():
        return [DepEmtpy]


class DepOne2(Dependant):

    @staticmethod
    def dependencies():
        return [DepEmtpy]


class DepTwo(Dependant):

    @staticmethod
    def dependencies():
        return [DepOne, DepOne2]


class TestDependencySolver(unittest.TestCase):

    def __init__(self, *args) -> None:
        super().__init__(
            *args,
        )

    def test_single_dep(self) -> None:
        depone_instance = DepOne()

        # DepEmtpy should be added before
        solution = DependencySolver(depone_instance).solve()
        self.assertEqual(len(solution), 2, 'solution length invalid')
        self.assertIsInstance(solution[0], DepEmtpy)
        self.assertIs(solution[1], depone_instance)

    def test_single_dep_existing(self) -> None:
        depempty_instance = DepEmtpy()
        depone_instance = DepOne()

        # Already in order
        solution = DependencySolver(depempty_instance, depone_instance).solve()
        self.assertEqual(len(solution), 2, 'solution length invalid')
        self.assertIs(solution[0], depempty_instance, 'wrong solution order')
        self.assertIs(solution[1], depone_instance, 'wrong solution order')

        # Out of order
        solution = DependencySolver(depone_instance, depempty_instance).solve()
        self.assertEqual(len(solution), 2, 'solution length invalid')
        self.assertIs(solution[0], depempty_instance, 'solution does not use existing instance')
        self.assertIs(solution[1], depone_instance, 'solution does not use existing instance')

    def test_duplicate_dependency(self) -> None:
        deptwo_instance = DepTwo()

        # DepOne and DepOne2 both depend on DepEmpty
        solution = DependencySolver(deptwo_instance).solve()
        self.assertEqual(len(solution), 4, 'solution length invalid')
        self.assertIsInstance(solution[0], DepEmtpy)
        self.assertIsInstance(solution[1], DepOne)
        self.assertIsInstance(solution[2], DepOne2)
        self.assertIs(solution[3], deptwo_instance)

        # Existing instance of DepEmpty, in order
        depempty_instance = DepEmtpy()
        solution = DependencySolver(depempty_instance, deptwo_instance).solve()
        self.assertEqual(len(solution), 4, 'solution length invalid')
        self.assertIsInstance(solution[0], DepEmtpy)
        self.assertIsInstance(solution[1], DepOne)
        self.assertIsInstance(solution[2], DepOne2)
        self.assertIs(solution[3], deptwo_instance)

        # Existing instance of DepEmpty, not in order
        solution = DependencySolver(deptwo_instance, depempty_instance).solve()
        self.assertEqual(len(solution), 4, 'solution length invalid')
        self.assertIsInstance(solution[0], DepEmtpy)
        self.assertIsInstance(solution[1], DepOne)
        self.assertIsInstance(solution[2], DepOne2)
        self.assertIs(solution[3], deptwo_instance)

    def test_kwargs(self) -> None:
        depone_instance = DepOne()

        # Pass parameter and check that the new instance has it
        solution = DependencySolver(depone_instance, myparam='myvalue').solve()
        self.assertEqual(len(solution), 2, 'solution length invalid')
        self.assertEqual(solution[0].myparam, 'myvalue', 'parameter not passed on')  # type: ignore


if __name__ == '__main__':
    unittest.main()
