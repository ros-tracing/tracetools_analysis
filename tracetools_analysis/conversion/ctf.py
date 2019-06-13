# CTF to pickle conversion

import babeltrace

# List of ignored CTF fields
_IGNORED_FIELDS = [
    'content_size', 'cpu_id', 'events_discarded', 'id', 'packet_size', 'packet_seq_num',
    'stream_id', 'stream_instance_id', 'timestamp_end', 'timestamp_begin', 'magic', 'uuid', 'v'
]
_DISCARD = 'events_discarded'


def ctf_to_pickle(trace_directory, target):
    """
    Load CTF trace and convert to a pickle file.

    :param trace_directory (str): the main/top trace directory
    :param target (Pickler): the target pickle file to write to
    """
    # add traces
    tc = babeltrace.TraceCollection()
    print(f'Importing trace directory: {trace_directory}')
    tc.add_traces_recursive(trace_directory, 'ctf')

    count = 0
    count_written = 0
    # count_pid_matched = 0
    # traced = set()

    # PID_KEYS = ['vpid', 'pid']
    for event in tc.events:
        count += 1
        # pid = None
        # for key in PID_KEYS:
        #     if key in event.keys():
        #         pid = event[key]
        #         break

        # Write all for now
        pod = _ctf_event_to_pod(event)
        target.dump(pod)
        count_written += 1

    return count_written


def _ctf_event_to_pod(ctf_event):
    """
    Convert name, timestamp, and all other keys except those in IGNORED_FIELDS into a dictionary.

    :param ctf_element: The element to convert
    :type ctf_element: babeltrace.Element
    :return:
    :return type: dict
    """
    pod = {'_name': ctf_event.name, '_timestamp': ctf_event.timestamp}
    if hasattr(ctf_event, _DISCARD) and ctf_event[_DISCARD] > 0:
        print(ctf_event[_DISCARD])
    for key in [key for key in ctf_event.keys() if key not in _IGNORED_FIELDS]:
        pod[key] = ctf_event[key]
    return pod
