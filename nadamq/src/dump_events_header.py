# -*- encoding: utf-8 -*-
import sys
import re
from io import StringIO
from typing import TextIO, Optional
from argparse import ArgumentParser

from path_helpers import path


def generate_ragel_events_header(input_path: str, output: TextIO) -> TextIO:
    print('''\
#ifndef ___PACKET_SOCKET_EVENTS__HPP___
#define ___PACKET_SOCKET_EVENTS__HPP___

#include <string>

inline std::string event_label(uint8_t event) {
  switch (event) {
''', file=output)

    with open('packet_socket_fsm.rl', 'rb') as input_file:
        cre_event = re.compile(r"^\s+(?P<label>\w+).*(?P<char>'.');", re.MULTILINE)
        for label, char in cre_event.findall(input_file.read().decode()):
            print(f'''    case {char}: return "{label}";''', file=output)

    print('''
    default: return "<unknown event>";
  }
}

#endif  // #ifndef ___PACKET_SOCKET_EVENTS__HPP___
''', file=output)
    return output


def parse_args(argv: Optional[sys.argv] = None):
    """Parses arguments, returns (options, args)."""
    if argv is None:
        argv = sys.argv[1:]

    parser = ArgumentParser(description='Generate a C++ header containing '
                                        'labels for event characters from a Ragel FSM '
                                        'definition.')
    parser.add_argument('-f', '--force_overwrite', action='store_true',
                        default=False)
    parser.add_argument('-o', '--output_path', type=path, default=None)
    parser.add_argument(dest='input_file', type=path)
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args()
    if args.output_path is None:
        output = StringIO()
    else:
        if args.output_path.isfile() and not args.force_overwrite:
            # The output-path exists, but `overwrite` was not enabled, so raise
            # exception.
            raise IOError(f'Output path `{args.output_path}` already exists. '
                          f'Specify `overwrite=True` to force overwrite.')
        output = args.output_path.open('wb')
    try:
        generate_ragel_events_header(args.input_file, output)
    finally:
        if args.output_path is not None:
            output.close()
        else:
            print(output.getvalue())
