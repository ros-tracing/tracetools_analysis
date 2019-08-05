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

"""Module for profile events processing."""

from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type
from typing import Union

from tracetools_read import get_field

from . import EventHandler
from . import EventMetadata

from ..data_model.profile import ProfileDataModel


class ProfileHandler(EventHandler):
    """
    Handler that extracts profiling information.

    It uses the following events:
        * lttng_ust_cyg_profile_fast:func_entry
        * lttng_ust_cyg_profile_fast:func_exit
    """

    FUNCTIONS = {
        'get_next_ready_executable': [],
        'wait_for_work': [
            'collect_entities',
            'add_handles_to_wait_set',
            'rmw_wait',
            'remove_null_handles',
        ],
    }

    def __init__(
        self,
        *,
        functions: Dict[str, List[str]] = FUNCTIONS,
        **kwargs,
    ) -> None:
        handler_map = {
            'lttng_ust_cyg_profile_fast:func_entry':
                self._handle_function_entry,
            'lttng_ust_cyg_profile_fast:func_exit':
                self._handle_function_exit,
        }
        super().__init__(handler_map=handler_map, **kwargs)

        self._data = ProfileDataModel()
        self.functions = functions

        # Temporary buffers
        # tid ->
        #   (list of functions currently executing (ordered by relative depth),
        #    start timestamp of the function)
        self._current_funcs: Dict[int, List[Tuple[str, int]]] = defaultdict(list)

        # TODO get debug_info from babeltrace for
        # lttng_ust_cyg_profile_fast:func_entry events
        # (or resolve { address -> function } name another way)
        self.address_to_func = {
            int('0x7F6CD676CDB4', 16): 'get_next_ready_executable',
            int('0x7F6CD676BC54', 16): 'wait_for_work',
            int('0x7F6CD678D0F8', 16): 'collect_entities',
        }

    def get_data_model(self) -> ProfileDataModel:
        return self._data

    def _handle_function_entry(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        function_name = self._get_function_name(event)
        assert function_name is not None, f'cannot resolve function name for event: {event}'
        # Push function data to stack
        self._current_funcs[metadata.tid].append(
            (metadata.timestamp, function_name)
        )

    def _handle_function_exit(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        # Pop function data from stack
        tid = metadata.tid
        tid_functions = self._current_funcs[tid]
        function_depth = len(tid_functions) - 1
        (start_timestamp, start_function_name) = tid_functions.pop()
        # Add to data model
        parent_name = tid_functions[-1][1] if function_depth > 0 else None
        duration = metadata.timestamp - start_timestamp
        self._data.add_duration(
            tid,
            function_depth,
            start_function_name,
            parent_name,
            start_timestamp,
            duration
        )

    def _get_function_name(
        self, event: Dict
    ) -> str:
        address = get_field(event, 'addr')
        return self._resolve_function_address(address)
        # return address

    def _resolve_function_address(
        self, address: int
    ) -> Union[str, None]:
        # TODO get from trace/binaries
        return self.address_to_func.get(address, None)
