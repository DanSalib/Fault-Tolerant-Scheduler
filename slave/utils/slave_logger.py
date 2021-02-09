import logging
import os
import sys

from datetime import datetime

CONTAINER_LOGS_FOLDER = 'slave/slave_logs'


def slave_logger(name, host):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    f_handler = logging.FileHandler(os.path.join(
        CONTAINER_LOGS_FOLDER, '_'.join(['slave', host])))

    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    return logger
