import shutil

from logger import g_logger


class CopyFilePolicy(object):
    def __init__(self):
        pass

    @staticmethod
    def copy(src, dest):
        g_logger.info("Copy: %s -> %s" % (src, dest))
        shutil.copy(src, dest)

    @staticmethod
    def delete_duplicated(dest):
        pass

