import os
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from logger import g_logger
from policy import DefaultFilePolicy, SafeFilePolicy, DebugFilePolicy, FilePolicyBase
from storage import MemoryStorage


def get_context():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-s', '--source', required=True,
                            help="Source folder with files, which needs to be split.")
    arg_parser.add_argument('-o', '--output', default=None,
                            help="Output folder where split files will be. By default will be place near source folder.")

    arg_parser.add_argument('-s', '--safe', dest='transfer_policy', action='store_const', const='safe',
                            help="Files will be copied into output folder.")
    arg_parser.add_argument('-d', '--debug', dest='transfer_policy', action='store_const', const='debug',
                            help="Files will be copied into output folder.")

    arg_parser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                            default='info', help="Log level for logger.")

    arg_parser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")

    return arg_parser.parse_args()


def main(context):
    g_logger.setLevel(context.log_level.upper())
    g_logger.debug(context)

    assert context.source is not None

    source_dir: Path = Path(context.source)
    if context.output is None:
        target_dir = source_dir.parent.joinpath(f'{source_dir.name}_sorted')
    else:
        target_dir: Path = Path(context.output)

    policy: FilePolicyBase = DefaultFilePolicy()
    if context.transfer_policy == 'safe':
        safe_dir = source_dir.parent.joinpath(f'{source_dir.name}_safe')
        policy = SafeFilePolicy(safe_dir)
    elif context.transfer_policy == 'debug':
        policy = DebugFilePolicy()

    storage = MemoryStorage(source_dir, target_dir, policy)
    storage.remove_duplicated()
    storage.separate(context.path_pattern)


if __name__ == "__main__":
    main(get_context())
fi