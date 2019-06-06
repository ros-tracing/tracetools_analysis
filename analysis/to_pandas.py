# Convert processor object to pandas dataframe

import pandas as pd
from .ros_processor import RosProcessor

def callback_durations_to_df(ros_processor):
    callback_addresses = []
    durations = []
    for addr in ros_processor.callbacks_instances:
        for d in ros_processor.callbacks_instances[addr]:
            callback_addresses.append(addr)
            durations.append(d)

    return pd.DataFrame(data={
        'callback_address': callback_addresses,
        'duration': durations,
    })
