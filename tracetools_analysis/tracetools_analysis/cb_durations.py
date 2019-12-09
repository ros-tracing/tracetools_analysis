#! /usr/bin/python

import pandas as pd

from tracetools_analysis.loading import load_file
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil

import sys

removals = [
    "void (", "rclcpp::", "std::shared_ptr<", ">", "::msg"
]
replaces = [
    ("?)", "?")
]


def format_fn(fname: str):
    for r in removals:
        fname = fname.replace(r, "")
    for a, b in replaces:
        fname = fname.replace(a, b)

    return fname

def main():
    if len(sys.argv) < 2:
        print("Syntax: <tracefile>")
        sys.exit(-1)

    events = load_file(sys.argv[1])
    handler = Ros2Handler.process(events)
    du = Ros2DataModelUtil(handler.data)

    stat_data = []
    for ptr, name in du.get_callback_symbols().items():
        durations = du.get_callback_durations(ptr)["duration"]        
        stat_data.append((durations.count(), durations.sum(), durations.mean(), durations.std(), format_fn(name)))
    
    stat_df = pd.DataFrame(columns=["Count", "Sum", "Mean", "Std", "Name"], data=stat_data)
    print(stat_df.sort_values(by="Sum", ascending=False).to_string())
        