#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from flask import request
from logging import Formatter
import logging
import logging.handlers

class RequestFormatter(Formatter):
    def format(self, record):
        try:
            record.url = '{} {}'.format(request.method, request.path)
        except Exception as e:
            record.url = ''
        return super().format(record)

def create_logger():
    """创建日志"""
    #  logger = app.logger

    logger = logging.getLogger('tmdapi')
    logger.setLevel(logging.DEBUG)

    fmt = '[%(asctime)s] [%(filename)s:%(lineno)d\t] [%(levelname)s] '\
            '[%(url)s\t] %(message)s '
    fmt = RequestFormatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    #  file_handler = logging.handlers.RotatingFileHandler(
        #  'log/tmd-debug.log', maxBytes=104857600, backupCount=20
            #  )
    #  file_handler.setFormatter(fmt)
    #  file_handler.setLevel(logging.DEBUG)
    #  logger.addHandler(file_handler)

    error_file_handler = logging.handlers.RotatingFileHandler(
        'log/tmd-error.log', maxBytes=104857600, backupCount=20
            )
    error_file_handler.setFormatter(fmt)
    error_file_handler.setLevel(logging.ERROR)
    logger.addHandler(error_file_handler)

    return logger
