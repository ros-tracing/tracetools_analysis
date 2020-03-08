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
from typing import Set
from typing import Union

from tracetools_read import get_field

from . import EventHandler
from . import EventMetadata
from . import HandlerMap
from ..data_model.profile import ProfileDataModel


class ProfileHandler(EventHandler):
    """
    Handler that extracts profiling information.

    It uses the following events:
        * lttng_ust_cyg_profile_fast:func_entry
        * lttng_ust_cyg_profile_fast:func_exit
        * sched_switch

    The above events are generated when using -finstrument-functions with gcc and LD_PRELOAD-ing
    liblttng-ust-cyg-profile-fast.so, see:
    https://lttng.org/docs/v2.10/#doc-liblttng-ust-cyg-profile

    TODO get debug_info from babeltrace for
    lttng_ust_cyg_profile_fast:func_entry events
    (or resolve { address -> function } name another way)
    """

    def __init__(
        self,
        address_to_func: Dict[Union[int, str], str] = {},
        **kwargs,
    ) -> None:
        """
        Create a ProfileHandler.

        :param address_to_func: the mapping from function address (`int` or hex `str`) to name
        """
        handler_map: HandlerMap = {
            'lttng_ust_cyg_profile_fast:func_entry':
                self._handle_function_entry,
            'lttng_ust_cyg_profile_fast:func_exit':
                self._handle_function_exit,
            'sched_switch':
                self._handle_sched_switch,
        }
        super().__init__(
            handler_map=handler_map,
            data_model=ProfileDataModel(),
            **kwargs,
        )

        self._address_to_func = {
            self.addr_to_int(addr): name for addr, name in address_to_func.items()
        }

        # Temporary buffers
        # tid ->
        #   list:[
        #           functions currently executing (ordered by relative depth), with info:
        #           [
        #               function name,
        #               start timestamp,
        #               last execution start timestamp of the function,
        #               total duration,
        #           ]
        #        ]
        self._current_funcs: Dict[int, List[List[Union[str, int]]]] = defaultdict(list)

    @staticmethod
    def required_events() -> Set[str]:
        return {
            'lttng_ust_cyg_profile_fast:func_entry',
            'lttng_ust_cyg_profile_fast:func_exit',
            'sched_switch',
        }

    @property
    def data(self) -> ProfileDataModel:
        return super().data  # type: ignore

    @staticmethod
    def addr_to_int(addr: Union[int, str]) -> int:
        """Transform an address into an `int` if it's a hex `str`."""
        return int(addr, 16) if isinstance(addr, str) else addr

    def _handle_sched_switch(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        timestamp = metadata.timestamp
        # If function(s) currently running stop(s) executing
        prev_tid = get_field(event, 'prev_tid')
        prev_info_list = self._current_funcs.get(prev_tid, None)
        if prev_info_list is not None:
            # Increment durations using last start timestamp
            for info in prev_info_list:
                last_start = info[2]
                total_duration = info[3]
                total_duration += timestamp - last_start
                info[2] = -1
                info[3] = total_duration
        # If stopped function(s) start(s) executing again
        next_tid = get_field(event, 'next_tid')
        next_info_list = self._current_funcs.get(next_tid, None)
        if next_info_list is not None:
            # Set last start timestamp to now
            for info in next_info_list:
                assert info[2] == -1
                info[2] = timestamp

    def _handle_function_entry(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        function_name = self._get_function_name(event)
        # Push function data to stack, setting both timestamps to now
        self._current_funcs[metadata.tid].append([
            function_name,
            metadata.timestamp,
            metadata.timestamp,
            0,
        ])

    def _handle_function_exit(
        self, event: Dict, metadata: EventMetadata
    ) -> None:
        # Pop function data from stack
        tid = metadata.tid
        tid_functions = self._current_funcs[tid]
        function_depth = len(tid_functions) - 1
        info = tid_functions.pop()
        function_name = info[0]
        start_timestamp = info[1]
        last_start_timestamp = info[2]
        total_duration = info[3]
        # Add to data model
        parent_name = tid_functions[-1][0] if function_depth > 0 else None
        duration = metadata.timestamp - start_timestamp
        actual_duration = (metadata.timestamp - last_start_timestamp) + total_duration
        self.data.add_duration(
            tid,
            function_depth,
            function_name,  # type: ignore
            parent_name,  # type: ignore
            start_timestamp,  # type: ignore
            duration,
            actual_duration,
        )

    def _get_function_name(
        self, event: Dict
    ) -> str:
        address = get_field(event, 'addr')
        resolution = self._resolve_function_address(address)
        if resolution is None:
            resolution = self.int_to_hex_str(address)
        return resolution

    def _resolve_function_address(
        self, address: int
    ) -> Union[str, None]:
        return self._address_to_func.get(address, None)
