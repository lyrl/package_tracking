#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-07-26 11:04:34
import logging


def get_logger(name):
    logger = logging.getLogger(name)

    try:
        while logger.handlers.pop():
            continue
    except IndexError as i:
        pass


    handler = logging.StreamHandler()
    formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formater)
    logger.addHandler(handler)

    # file_handler = logging.FileHandler("youxia.log")
    # formatter = logging.Formatter(
    #     '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    #
    logger.setLevel(logging.DEBUG)

    return logger
