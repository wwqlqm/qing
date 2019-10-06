from datetime import datetime

import traceback
import os
import time

from common.base import BaseResponse
from common.config import app
from common.config import logger
from common.config import init_views

from flask import g
from flask import request



@app.before_request
def init_request_data():
    g.request_start_time = time.time()
    g.api_id = int(g.request_start_time * 1000)
    if app.config['DEBUG']:
        try:
            data = request.data
            args = request.args or {}
            #  json_data = request.json or {}
            #  form_data = request.form or {}
            h_data = request.headers or {}

            logger.debug('{} Request Begin ID'.format('-' * 10))
            logger.debug('{} {}'.format(request.method, request.url))

            logger.debug('Header %s', dict(h_data))
            logger.debug('Data   %s', data)
        except Exception as e:
            logger.error('params %s', e)
            logger.error(traceback.format_exc())


@app.after_request
def after_request(response):
    if not hasattr(g, 'request_start_time'):
        return response
    elapsed = time.time() - g.request_start_time
    logger.debug('%s Request End    time_used: %s', '-' * 10, elapsed)
    return response

@app.errorhandler(Exception)
def app_error_handler(e):
    logger.error(e)
    logger.error(traceback.format_exc())
    return BaseResponse.return_internal_server_error(str(e))

init_views('myself/views', '/myself/v1')
