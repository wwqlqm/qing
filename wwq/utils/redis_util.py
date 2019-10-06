#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import os
import redis
import traceback
from config.config import app
from config.config import logger
from utils import utils

HOST = os.getenv("REDIS_HOST") or app.config['REDIS_HOST']
logger.debug(HOST)

class Redis():
    def __init__(self, host=HOST,
            port=app.config['REDIS_PORT']):
        pool = redis.ConnectionPool(host=host, port=port, db=0)
        self.client = redis.Redis(connection_pool=pool)

    def incr(self, key):
        return self.client.incr(key)

    def delete(self, *keys):
        return self.client.delete(*keys)

    def set(self, name, value, **kwargs):
        """
        kwargs:
            ex: 时效
        """
        value = utils.sequence(value)
        return self.client.set(name=name, value=value, **kwargs)

    def watch_set(self, name, value, **kwargs):
        """
        kwargs:
            ex: 时效
        """
        value = utils.sequence(value)
        self.client.watch()
        self.client.multi()
        return self.client.set(name=name, value=value, **kwargs)

    def get(self, name):
        res = self.client.get(name)
        try:
            res = utils.unsequence(res)
            return res
        except:
            logger.error(res)
            logger.error(traceback.format_exc())
            return None

    def get_incr(self, key):
        res = self.client.get(key)
        if not res:
            return 0
        res = int(res.decode('utf-8'))
        return res

    def keys(self, key_pattern):
        keys = self.client.keys(key_pattern)
        res = [o.decode() for o in keys]
        return res

    def lpush(self, name, *values):
        if not values:
            return 0
        seqs = []
        for v in values:
            val = utils.sequence(v)
            seqs.append(val)
        return self.client.lpush(name, *seqs)

    def rpush(self, name, *values):
        if not values:
            return 0
        seqs = []
        for v in values:
            val = utils.sequence(v)
            seqs.append(val)
        return self.client.rpush(name, *seqs)

    def lrange(self, name, begin, end):
        values = self.client.lrange(name, begin, end)
        vals = []
        for v in values:
            val = utils.unsequence(v)
            vals.append(val)
        return vals

    def llen(self, name):
        return self.client.llen(name)

    def lpop(self, name):
        return self.client.lpop(name)

    def rpop(self, name):
        return self.client.rpop(name)

    def geoadd(self, name, *values):
        return self.client.geoadd(name, *values)

    def geodist(self, name, place1, place2, unit='km'):
        try:
            return self.client.geodist(name, place1, place2, unit)
        except Exception as e:
            logger.error(e)
            return 0

    def georadius(self, name, longitude, latitude, radius, unit='km',
                  withdist=True, withcoord=False, withhash=False, count=11,
                  sort='ASC', store=None, store_dist=None):
        try:
            kw = locals()
            kw.pop('self')
            return self.client.georadius(**kw)
        except Exception as e:
            logger.error(e)
            return []

if __name__ == "__main__":
    r = Redis()
     #  for i in range(0,100):
        #  oid = r.incr('oid')
        #  print(oid, type(oid))
     #  client = r.client
     #  client.set(name='tt', value=11, ex=100)
     #  client.expire('tt', 30)
     #  print(client.get)
     #  keys = client.keys('oid:*')
     #  print(keys)
     #  client.lpush('test')
     #  r.lpush("testlpush1", 1, 2)
     #  r.rpush("testlpush1", {"name": "wxnacy"}, {"name": "wen"})

     #  r.lpop("testlpush1")
     #  r.rpop("testlpush1")
     #  print(r.lrange("testlpush1", 0, 15))
     #  r.client.lpop("testlpush")

    #  key = 'testlpush2'
    #  for i in range(18):
        #  r.lpush(key, i)
        #  if r.llen(key) > 3:
            #  r.rpop(key)
    #  print(r.lrange(key, 0, 15))
    #  print(r.llen(key))

    #  print(r.lrange('topic:recent:screen_AA7EIV', 0, 3))
    #  r.client.geoadd('geo_screen', -75.029145, 40.102175, 'A464')
