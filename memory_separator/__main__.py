import os
from argparse import ArgumentParser
from datetime import datetime

from logger import g_logger
from policy import MoveFilePolicy, CopyFilePolicy
from separator import remove_duplicated, separate


def get_context():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-sep', '--separate', dest='action',  action='store_const', const=separate, default=separate,
                            help="Separate files by dates.")
    arg_parser.add_argument('-rem', '--remove_duplicated', dest='action',  action='store_const', const=remove_duplicated,
                            help="Remove duplicated files")
    arg_parser.add_argument('-s', '--source', required=True,
                            help="Source folder with files, which needs to be split.")
    arg_parser.add_argument('-o', '--output', default=None,
                            help="Output folder where split files will be. By default will be place near source folder.")

    arg_parser.add_argument('-m', '--move', dest='transfer_policy', action='store_const',
                            default=MoveFilePolicy(), const=MoveFilePolicy(),
                            help="Files will be moved from source folder into output folder. It's default value.")

    arg_parser.add_argument('-c', '--copy', dest='transfer_policy', action='store_const', const=CopyFilePolicy(),
                            help="Files will be copied into output folder.")

    arg_parser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                            default='info', help="Log level for logger.")

    arg_parser.add_argument('-ext', '--extensions', nargs='+', help="Ignore file extensions.")
    arg_parser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")

    return arg_parser.parse_args()


def main(context):
    g_logger.debug(context)

    if context.output is None:
        assert context.source is not None

        source_dirname = os.path.dirname(context.source)
        context.output = os.path.normpath(os.path.join(context.source, '..', '{}_sorted'.format(source_dirname)))

    g_logger.setLevel(context.log_level.upper())

    start_time = datetime.now()
    g_logger.info(" - [Start]")
    context.action(context)
    g_logger.info(" - [End %s]" % (datetime.now() - start_time))


if __name__ == "__main__":
    main(get_context())
