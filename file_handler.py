# coding: utf-8
import argparse

import platformio_helpers as pioh

from path_helpers import path

NADAMQ_HEADERS = ['NadaMQ.h', 'output_buffer.h', 'packet_handler.h']
PACKET_HEADERS = ['BufferAllocator.h',
                  'Packet.h',
                  'PacketAllocator.h',
                  'PacketHandler.h',
                  'PacketParser.h',
                  'PacketSocket.h',
                  'PacketSocketEvents.h',
                  'PacketStream.h',
                  'PacketWriter.h',
                  'SimpleCommand.h',
                  'StreamPacketParser.h',
                  'crc-16.cpp',
                  'crc-16.h',
                  'crc_common.cpp',
                  'crc_common.h',
                  'packet_actions.cpp']


def create_cpp_from_ragel(source_dir: str, prefix: str, module_name: str) -> None:
    import subprocess
    import platform

    source_dir = path(source_dir).joinpath(module_name, 'src')
    prefix = path(prefix)

    if platform.system() == 'Windows':
        ragel = prefix.joinpath('Library', 'bin', 'ragel.exe')
    else:
        ragel = prefix.joinpath('bin', 'ragel')

    # Try installing ragel separately
    if not ragel.isfile():
        ragel = 'ragel'

    for source in source_dir.walkfiles('*.rl'):
        target = source.with_suffix('.cpp')
        subprocess.run([ragel, '-G2', '-o', target, source])
        print(f"Generated {target}")


def transfer(source_dir: str, module_name: str, lib_name: str) -> None:
    source_dir = path(source_dir).joinpath(module_name, 'src')
    install_dir = pioh.conda_arduino_include_path().joinpath(lib_name)
    install_dir.makedirs(exist_ok=True)

    for file_i in NADAMQ_HEADERS:
        src_file = source_dir.joinpath('Arduino', 'packet_handler', file_i)
        dst_file = install_dir.joinpath(src_file.name)
        src_file.copy2(dst_file)
        print(f"Copied '{src_file}' to '{dst_file}'")

    for file_i in PACKET_HEADERS:
        src_file = source_dir.joinpath(file_i)
        dst_file = install_dir.joinpath(file_i)
        src_file.copy2(dst_file)
        print(f"Copied '{src_file}' to '{dst_file}'")


def cli_parser():
    parser = argparse.ArgumentParser(description='Transfer header files to include directory.')
    parser.add_argument('source_dir', help='Source directory containing header files')
    parser.add_argument('prefix', help='Source directory containing header files')
    parser.add_argument('module_name', help='Source directory containing header files')
    parser.add_argument('lib_name', help='Source directory containing header files')

    args = parser.parse_args()

    create_cpp_from_ragel(args.source_dir, args.prefix, args.module_name)
    transfer(args.source_dir, args.module_name, args.lib_name)


if __name__ == '__main__':
    cli_parser()
