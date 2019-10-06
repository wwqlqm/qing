from utils import loggers
from utils import databases
from enum import Enum
from enum import unique
from werkzeug.contrib.fixers import ProxyFix
from logging import Formatter
import os
import logging
import logging.handlers
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from celery import Celery

import inspect
import importlib
CONFIG_NAME_MAPPER = {
    'local': 'config.config.LocalConfig',
    'product': 'local_config.ProductionConfig',
    'dev': 'local_config.DevelopmentConfig',
    'test': 'local_config.TestingConfig'
}

class LocalConfig():
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ganen123@59.110.161.241:3306/tmdaddev?charset=utf8mb4'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/local_ad?charset=utf8mb4'
    SLAVE_SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 100
    SQLALCHEMY_MAX_OVERFLOW = 200
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_AUTOFLUSH = False
    SQLALCHEMY_ECHO = False

    REDIS_HOST = 'localhost'
    REDIS_PORT = '6379'
    CELERY_BROKER_URL = 'redis://{}:6379'.format(REDIS_HOST)
    CELERY_RESULT_BACKEND = 'redis://{}:6379'.format(REDIS_HOST)


def create_app(flask_config_name=None):
    """
    创建配置
    :return:
    """
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    env_flask_config_name = os.getenv('FLASK_CONFIG')
    config_mapper_name = flask_config_name or env_flask_config_name or 'local'
    config_name = CONFIG_NAME_MAPPER[config_mapper_name]
    app.config.from_object(config_name)
    print('-------------------------init app-------------------------')
    return app

def init_views(dirname, url_prefix):
    views_path = '{}/{}/'.format(os.getcwd(), dirname)
    logger.debug(views_path)
    views_files = list(filter(
        lambda x: not x.startswith('__') and not x.startswith('.') and '.swp' not in x and '.swo' not in x,
        os.listdir(views_path)))
    logger.debug(views_files)
    for path in views_files:
        module_name = '{}.{}'.format(dirname.replace('/', '.'), path[0:-3])
        views_module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(views_module):
            if obj.__class__.__name__ == 'Blueprint':
                url_prefix = url_prefix
                app.register_blueprint(obj, url_prefix = url_prefix)

app = create_app()
logger = loggers.create_logger()
CORS(app)
db = SQLAlchemy(app)
slave_db = databases.DB(app)

cache = Cache(app, config={
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 300,                    # 全局过期时间
    # key 前缀，key 为 redis_cache_view/{route}
    "CACHE_KEY_PREFIX": "tmdcache_",
    "CACHE_REDIS_HOST": app.config.get("REDIS_HOST"),
    "CACHE_REDIS_PORT": app.config.get("REDIS_PORT"),
})

def make_cache_key(*args, **kw):
    path = request.path
    k1 = str(hash(frozenset(request.args.items())))
    k2 = str(hash(request.data))
    return '{}-{}-{}'.format(path, k1, k2)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)