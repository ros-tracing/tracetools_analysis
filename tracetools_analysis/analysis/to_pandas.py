# Convert processor object to pandas dataframe

import pandas as pd


def callback_durations_to_df(ros_processor):
    callback_addresses = []
    durations = []
    start_timestamps = []
    for addr in ros_processor.callbacks_instances:
        for duration, start in ros_processor.callbacks_instances[addr]:
            callback_addresses.append(addr)
            durations.append(duration)
            start_timestamps.append(start)

    return pd.DataFrame(data={
        'callback_address': callback_addresses,
        'duration': durations,
        'start_timestamp': start_timestamps
    })
