from argparse import ArgumentParser
from pathlib import Path

from memory.interactive_policy import ConsolePolicy
from memory.logger import g_logger
from memory.file_policy import DefaultFilePolicy, SafeFilePolicy, DebugFilePolicy, FilePolicyBase
from memory.storage import MemoryStorage


def get_context():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--separate', dest='action', action='store_const', const='separate',
                            help="Separate files by original date.")
    arg_parser.add_argument('--remove-duplicated', dest='action', action='store_const', const='remove_duplicated',
                            help="Remove all duplicated files.")
    arg_parser.add_argument('--video-compress', dest='action', action='store_const', const='video_compress',
                            help="Compress video files.")
    arg_parser.add_argument('--video-overview', dest='action', action='store_const', const='video_overview',
                            help="Overview video files.")

    arg_parser.add_argument('-s', '--source', required=True,
                            help="Source folder with files, which needs to be split.")
    arg_parser.add_argument('-o', '--output', default=None,
                            help="Output folder where split files will be. By default will be place near source folder.")

    arg_parser.add_argument('--safe', dest='transfer_policy', action='store_const', const='safe', default='safe',
                            help="Files will be copied into output folder.")
    arg_parser.add_argument('--debug', dest='transfer_policy', action='store_const', const='debug',
                            help="Files will be copied into output folder.")

    arg_parser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                            default='info', help="Log level for logger.")

    arg_parser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")
    arg_parser.add_argument('-i', '--ignore', action='append')

    return arg_parser.parse_args()


def main(context):
    g_logger.setLevel(context.log_level.upper())
    g_logger.info(context)

    assert context.source is not None

    source_dir: Path = Path(context.source).absolute()
    if context.output is None:
        target_dir = source_dir.parent.joinpath(f'{source_dir.name}_sorted')
    else:
        target_dir: Path = Path(context.output).absolute()

    policy: FilePolicyBase = DefaultFilePolicy()
    if context.transfer_policy == 'safe':
        safe_dir = source_dir.parent.joinpath(f'{source_dir.name}_safe')
        policy = SafeFilePolicy(safe_dir)
    elif context.transfer_policy == 'debug':
        policy = DebugFilePolicy()

    g_logger.info('%s to %s', source_dir, target_dir)

    storage = MemoryStorage(source_dir, target_dir,
                            policy, ConsolePolicy(),
                            whitelist_extentions={'.jpg', '.avi', '.png', '.webp', '.mp4', '.nef', '.mpg'},
                            ignore_dirs=context.ignore)
    if context.action == 'remove_duplicated':
        storage.remove_duplicated()
    elif context.action == 'separate':
        storage.separate(context.path_pattern)
    elif context.action == 'video_compress':
        storage.video_compress()
    elif context.action == 'video_overview':
        storage.video_overview()
    else:
        assert False, context.action


if __name__ == "__main__":
    main(get_context())
