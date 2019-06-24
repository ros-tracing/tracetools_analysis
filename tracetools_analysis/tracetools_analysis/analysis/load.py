import pickle
from typing import Dict
from typing import List


def load_pickle(pickle_file_path: str) -> List[Dict]:
    """
    Load pickle file containing converted trace events.

    :param pickle_file_path: the path to the pickle file to load
    :return: the list of events read from the file
    """
    events = []
    with open(pickle_file_path, 'rb') as f:
        p = pickle.Unpickler(f)
        while True:
            try:
                events.append(p.load())
            except EOFError:
                break  # we're done

    return events
