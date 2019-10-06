#!/usr/bin/env python
# ! -*- coding:utf-8 -*-
"""base信息"""

__author__ = "wenxiaoning(wenxiaoning@gochinatv.com)"
__copyright__ = "Copyright of GoChinaTV (2017)."

from collections import namedtuple
from uuid import UUID
from datetime import date
from datetime import datetime
from datetime import time
import json
import requests
import pymysql.cursors
import time as t

from flask import jsonify
from flask import request
from flask import make_response
from flask import g
from sqlalchemy import desc
from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.config import app
from config.config import db
from config.config import slave_db
from config.config import logger

from utils.redis_util import Redis
from urllib.parse import urlparse
import traceback
from threading import Thread

URL_CONFIG = urlparse(app.config['SQLALCHEMY_DATABASE_URI'])
redis = Redis()


class BaseObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self):
        return json.loads(self.to_json())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def __str__(self):
        return self.to_json()


def extended_encoder(x):
    if isinstance(x, datetime):
        return int(x.timestamp())
    if isinstance(x, UUID):
        return str(x)
    if isinstance(x, date):
        return x.isoformat()
    if isinstance(x, time):
        return x.isoformat()
    return x


class BaseModel(object):
    """
    SQLAlchemy JSON serialization
    """
    RELATIONSHIPS_TO_DICT = False
    __tablename__ = None

    def __iter__(self):
        return self.to_dict().items()

    def to_dict(self, rel=None, backref=None, include=None, exclude=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: extended_encoder(getattr(self, attr))
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]

        return BaseDict(res).filter(source_include=include,
                                    source_exclude=exclude)

    def format(self):
        return self.to_dict()

    def to_json(self, rel=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        return json.dumps(self.to_dict(rel), default=extended_encoder)

    def __str__(self):
        return self.to_json()

    @classmethod
    def generate_id(cls):
        """生成id"""
        table_name = cls.__tablename__
        if not table_name:
            return None

        if table_name not in ['user', 'circle', 'article', 'comment', 'tag']:
            return None

        sql = "SELECT func_gen_auto_id(0,%s) as id;"

        res = BaseDB.query(sql, [table_name])
        if not res:
            return None

        return res[0]['id']

    @classmethod
    def return_not_found_msg(cls, item):
        return '{} {} is not found'.format(cls.__tablename__, item)

    @classmethod
    def create(cls, **params):
        item = cls(**params)
        db.session.add(item)
        db.session.commit()
        return item

    @classmethod
    def create_duplicate(cls, **params):
        insert_stmt = insert(cls).values(**params)
        on_conflict_stmt = insert_stmt.on_duplicate_key_update(
            **params
        )
        res = db.engine.execute(on_conflict_stmt)
        db.session.commit()
        lastrowid = res.lastrowid
        item = cls.query_by_id(lastrowid)
        return item

    @classmethod
    def create_items(cls, items: list):
        db.session.execute(cls.__table__.insert(), items)
        db.session.commit()

    def create_self(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def update_by_id(cls, id, **params):
        item = cls.query.filter_by(id=id, is_available=1).update(params)
        db.session.commit()
        return item

    def update_self(self):
        db.session.commit()
        return self

    @classmethod
    def get_or_create(cls, **params):
        params['is_available'] = 1
        item = cls.query.filter_by(**params).first()
        if not item:
            item = cls(**params)
            db.session.add(item)
            db.session.commit()
        return item

    @classmethod
    def query_or_create(cls, **params):
        item = cls.query_item(**params)
        if not item:
            item = cls.create(**params)
        return item

    @classmethod
    def query_item(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        return cls.query.filter_by(**params).order_by(
            desc(cls.create_ts)).first()

    @classmethod
    def slave_query_item(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        return slave_db.session.query(cls).filter_by(**params).order_by(
            desc(cls.create_ts)).first()

    @classmethod
    def query_by_id(cls, id):
        params = dict(id=id, is_available=1)
        return cls.query.filter_by(**params).first()

    @classmethod
    def slave_query_by_id(cls, id):
        params = dict(id=id, is_available=1)
        item = slave_db.session.query(cls).filter_by(**params).first()
        #  slave_db.session.remove()
        #  slave_db.session.commit()
        return item

    @classmethod
    def query_in_ids(cls, ids):
        params = dict(id=id, is_available=1)
        return cls.query.filter(cls.id.in_(ids), cls.is_available == 1
                                ).order_by(desc(cls.create_ts)).all()

    @classmethod
    def query_items(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        return cls.query.filter_by(**params).order_by(desc(cls.create_ts)).all()

    @classmethod
    def slave_query_items(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        items = slave_db.session.query(cls).filter_by(
            **params).order_by(desc(cls.create_ts)).all()
        #  slave_db.session.remove()
        return items

    @classmethod
    def query_items_plus(cls, condition="", params={}, order="create_ts desc"):
        if condition:
            condition = condition + " and is_available"
        else:
            condition = "is_available"

        return cls.query.filter(text(condition)).params(**params).order_by(order).all()

    @classmethod
    def query_paginate(cls, page, per_page, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        return cls.query.filter_by(**params).order_by(
            desc(cls.create_ts)).paginate(page, per_page, False)

    @classmethod
    def query_count(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        return cls.query.filter_by(**params).count()

    @classmethod
    def delete(cls, **params):
        if not params:
            params = {}
        params['is_available'] = 1
        item = cls.query.filter_by(**params).update(dict(is_available=0))
        db.session.commit()
        return item

    @classmethod
    def delete_in_ids(cls, ids: list):
        cls.query.filter(cls.id.in_(ids)).update(
            dict(is_available=0), synchronize_session=False)
        db.session.commit()

    @classmethod
    def update_in_ids(cls, ids: list, kwargs):
        cls.query.filter(cls.id.in_(ids)).update(kwargs,
                                                 synchronize_session=False)
        db.session.commit()

    def delete_self(self):
        self.is_available = 0
        db.session.commit()
        return self

    def update_ext(self, key, value):
        ext = dict(self.ext_property or {})
        ext[key] = value
        self.ext_property = ext
        self.update_self()
        return self

    def update_ext_dict(self, **kwargs):
        ext = dict(self.ext_property or {})
        ext.update(kwargs)
        self.ext_property = ext
        self.update_self()
        return self

    def get_ext(self, key):
        ext = dict(self.ext_property or {})
        return ext.get(key)

    def update_if_change(self, **kwargs):
        if not kwargs:
            return False
        is_update = False
        fields = []
        for k, v in kwargs.items():
            ov = getattr(self, k)
            if ov != v:
                setattr(self, k, v)
                fields.append('{}: {}'.format(k, v))
                is_update = True

        if is_update:
            logger.debug('{} need update {}'.format(repr(self),
                                                    fields))
            self.update_self()
            self.refresh_cache()
        return is_update

    def fmt_cache(self):
        return self.format()

    def refresh_cache(self, timeout=300, key=None):
        item = self.fmt_cache()
        if not key:
            key = self.get_cache_key(id=self.id)
            if self.__tablename__ == 'screen':
                key = self.get_cache_key(code=self.code)
        redis.set(key, item, ex=timeout)
        return item

    @classmethod
    def query_cache(cls, **kwargs):
        k = cls.get_cache_key(**kwargs)
        item = redis.get(k)
        if not item:
            s = cls.query_item_for_cache(**kwargs)
            if not s:
                return {}
            item = s.refresh_cache(key=k)
        return item

    @classmethod
    def query_item_for_cache(cls, **kwargs):
        return cls.slave_query_item(**kwargs)

    @classmethod
    def get_cache_key(cls, **kwargs):
        '''
        获取缓存 key
        '''
        if not kwargs:
            return None
        keys = list(kwargs.keys())
        keys.sort()
        key_suffix = ','.join([str(kwargs[o]) for o in keys])
        return 'cache_{}_{}'.format(cls.__tablename__, key_suffix)
        #  key_prefix = 'cache_{}'.format(cls.__tablename__)

        #  if 'id' in kwargs:
        #  return '{}_{}'.format(key_prefix, kwargs['id'])
        #  if 'code' in kwargs:
        #  return '{}_{}'.format(key_prefix, kwargs['code'])

    @classmethod
    def refresh_cache_all(cls, timeout=300, query={}, key_query={}):
        items = cls.slave_query_items(**query)
        key = None
        if key_query:
            key = cls.get_cache_key(**key_query)
        for item in items:
            item.refresh_cache(timeout=timeout, key=key)


class BaseDict(dict):
    def filter(self, *args, **kwargs):
        """
        过滤dict
        :param args: 默认 source_include
        :param kwargs:
            source_include：想要留下的keys
                eq:[attr,attr1]
                子元素可以使用 ["obj.attr"] 和 ["obj[attr1,attr2]"] 两种方式
                速度上推荐使用 ["obj[attr1,attr2]"]
            source_exclude：想要去掉的keys
        :return:
        """
        source_include = args if args else kwargs.get('source_include')
        source_exclude = kwargs.get('source_exclude')

        def _filter(t, o, k):
            """
            过滤key
            :param t: 过滤结果
            :param o: 目标对象
            :param k: 需要过滤的key
            :return:
            """
            if k in o:
                t[k] = o[k]
            return t

        def _check_key(t, o, k):
            """
            判断key需要何种过滤
            :param t: 过滤结果
            :param o: 目标对象
            :param k: 需要过滤的key
            :return:
            """
            if '.' in k:
                key = k.split('.', 1)[0]
                sub_key = k.split('.', 1)[1]
                if o.get(key) and isinstance(o.get(key), dict):
                    if key not in t:
                        t[key] = {}
                    t[key] = _check_key(t[key], o[key], sub_key)
            elif '[' in k and ']' in k:
                key = k.split('[')[0]
                v = o.get(key)
                sub_keys = k.split('[')[1].rstrip(']').split(',')
                if isinstance(v, dict):
                    t[key] = BaseDict(v).filter(*sub_keys)
                elif isinstance(v, list):
                    t[key] = [BaseDict(sv).filter(*sub_keys) for sv in v]
            else:
                t = _filter(t, o, k)

            return t

        temp = {}
        if source_include:
            for item in source_include:
                temp = _check_key(temp, self, item)
            return temp
        elif source_exclude:
            for item in source_exclude:
                self.pop(item)
            return self
        return self

    def __getattr__(self, item):
        return self[item]


class BaseDB(object):
    @classmethod
    def create_conn(cls):
        '''创建mysql链接'''
        return pymysql.connect(
            host=URL_CONFIG.hostname,
            port=URL_CONFIG.port,
            user=URL_CONFIG.username,
            password=URL_CONFIG.password,
            db=URL_CONFIG.path[1:],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @classmethod
    def query(cls, sql, params):
        """
        查询操作
        :param sql:
        :param params:
        :return:
        """
        conn = cls.create_conn()
        try:
            cursor = conn.cursor()

            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
            return result
        except BaseException as e:
            app.logger.error(traceback.format_exc())
            return []
        finally:
            conn.close()

    @classmethod
    def execute(cls, sql, params):
        """
        更新操作
        :param sql:
        :param params:
        :return:
        """
        conn = cls.create_conn()
        try:
            cursor = conn.cursor()

            result = cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return result
        except BaseException as e:
            app.logger.error(traceback.format_exc())
            return False
        finally:
            conn.close()

    @classmethod
    def query_db(cls, sql, **kwargs):
        res = db.engine.execute(text(sql), **kwargs)
        keys = res.keys()
        Record = namedtuple('Record', res.keys())
        records = {Record(*r) for r in res.fetchall()}
        return records
        #  res = [r for r in records]

        #  def _fmt_i(k, v):
        #  return k ,v

        #  def _fmt(o):
        #  r = list(map(_fmt_i, keys, o))
        #  return {k: v for k, v in r}
        #  res = [_fmt(o) for o in res.fetchall()]
        #  return res

    @classmethod
    def execute_db(cls, sql, **kwargs):
        res = db.engine.execute(text(sql), **kwargs)
        db.session.commit()
        return res

    @classmethod
    def executemany_db(cls, sql, *args):

        conn = cls.create_conn()
        try:
            cursor = conn.cursor()

            return True
        except BaseException as e:
            app.logger.error(traceback.format_exc())
            return False
        finally:
            conn.close()


class BaseResponse(BaseModel):
    CODE_UNKOWN = 1000
    CODE_UNBIND = 1001
    CODE_ERROR_SCREEN_CODE = 1002
    CODE_UNFOUND_SHOP = 1003
    CODE_ERROR_MOBILE_CODE = 1004

    #  data = {}
    #  status = 200
    #  message = ""
    #  version = 0
    #  error_code = 0

    def __init__(self, data={}, status=200, message="", error_code=200):
        self.data = data
        self.status = status
        self.message = message
        #  self.version = int(t.time())
        self.version = g.api_id
        self.error_code = error_code

    def to_dict(self, rel=None, backref=None, include=None, exclude=None):
        item = self.__dict__
        # print(item)
        # item['message'] = item['message'][0]
        return item

    def is_success(self):
        return self.status == 200

    def is_error(self):
        return self.status is not 200

    def return_self(self):
        return make_response(jsonify(self.to_dict()), self.status)

    @classmethod
    def return_response(cls, data={}, status=200, message="", headers={},
                        error_code=200):
        try:
            logger.debug('Return status %s %s', status, message)
        except:
            app.logger.error(traceback.format_exc())

        try:
            filters = request.args.get('filters')
            if filters:
                fd = BaseDict(data).filter(*filters.split(','))
                data = fd
        except:
            app.logger.error(traceback.format_exc())
            data = data

        try:
            if isinstance(data, db.Model):
                data = data.format()
            elif isinstance(data, list) and data and \
                    isinstance(data[0], db.Model):
                data = [o.format() for o in data]

        except:
            logger.error(traceback.format_exc())
            data = data

        res = cls(
            data=data,
            status=status,
            message=message,
            error_code=error_code
        ).to_dict()

        return make_response(jsonify(res), status, headers)

    @classmethod
    def return_success(cls, data={}):
        return cls.return_response(data)

    @classmethod
    def return_error(cls, status, message, error_code=1000):
        return cls.return_response(status=status, message=message,
                                   error_code=error_code)

    @classmethod
    def return_internal_server_error(cls, message='Internal Server Error'):
        return cls.return_response(status=500, message=message)

    @classmethod
    def return_unauthorized(cls, message='Unauthorized'):
        return cls.return_response(status=401, message=message)

    @classmethod
    def return_not_found(cls, message='Not Found'):
        return cls.return_response(status=404, message=message)

    @classmethod
    def return_forbidden(cls, message='Forbidden'):
        return cls.return_response(status=403, message=message)

    @classmethod
    def return_client_error(cls, error_code=1000,
                            message='Forbidden'):
        return cls.return_response(status=403, message=message,
                                   error_code=error_code)

    @classmethod
    def make_paginate(cls, data, total_size, page, size):
        """
        生成返回数据
        :param data:
        :param total_size:
        :param page:
        :param size:
        :return:
        """
        total_page = total_size // size
        yu = total_size % size
        if yu > 0:
            total_page += 1

        res = {
            "items": data,
            "cur_page": int(page),
            "total_items": total_size,
            "total_pages": total_page,
            "item_per_page": size
        }
        return res


class BaseRequest:
    @classmethod
    def get_param_int(cls, params, key, default=0):
        res = params.get(key, default)
        return int(res)


class BaseThread(Thread):
    def __init__(self, func, *args, **kwargs):
        super(BaseThread, self).__init__()
        self.func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self.func(*self._args, **self._kwargs)


class BaseSQLAlchemy():
    def __init__(self, *args, **kwargs):
        if args:
            self.database_uri = args[0]
        engine = create_engine(self.database_uri, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()

