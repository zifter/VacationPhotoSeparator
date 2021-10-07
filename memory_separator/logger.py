import logging


def setup_logger(name):
    logger = logging.getLogger(name)
    stream = logging.StreamHandler()
    logger.addHandler(stream)
    return logger


g_logger = setup_logger('separator')
