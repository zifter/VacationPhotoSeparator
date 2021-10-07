import shutil

from logger import g_logger


class MoveFilePolicy(object):
    def __init__(self):
        pass

    @staticmethod
    def copy(src, dest):
        g_logger.info("Move: %s -> %s" % (src, dest))
        shutil.move(src, dest)

    @staticmethod
    def delete_duplicated(dest):
        g_logger.info("Remove duplicated: %s" % dest)
        os.remove(dest)
