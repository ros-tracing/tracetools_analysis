#!/usr/bin/env python3
# Entrypoint/script to convert CTF trace data to a pickle file

import argparse
from pickle import Pickler

from tracetools_analysis.conversion import ctf


def parse_args():
    parser = argparse.ArgumentParser(description='Convert CTF trace data to a pickle file.')
    parser.add_argument('trace_directory',
                        help='the path to the main CTF trace directory')
    parser.add_argument('pickle_file',
                        help='the target pickle file to generate')
    return parser.parse_args()


def main():
    args = parse_args()

    trace_directory = args.trace_directory
    pickle_target_file = args.pickle_file

    with open(pickle_target_file, 'wb') as f:
        p = Pickler(f, protocol=4)
        ctf.ctf_to_pickle(trace_directory, p)
