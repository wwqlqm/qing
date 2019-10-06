#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


class DB():
    def __init__(self, app):
        #  self.session = session
        engine = create_engine(
            app.config['SLAVE_SQLALCHEMY_DATABASE_URI'],
            pool_size = app.config.get('SQLALCHEMY_POOL_SIZE'),
            max_overflow = app.config['SQLALCHEMY_MAX_OVERFLOW'],
            pool_recycle = app.config['SQLALCHEMY_POOL_RECYCLE'],
            #  isolation_level = 'AUTOCOMMIT',
            #  isolation_level = 'READ UNCOMMITTED',
            echo=app.config.get("SQLALCHEMY_ECHO") or False
        )


        #  self._Session = scoped_session(
        self.session = scoped_session(
            sessionmaker(
                bind=engine,
                autoflush = False,
                autocommit = True,
            )
        )

        #  self.session = self._Session()
        #  self.session = self._Session



#  def init_slave_db(app):
    #  engine = create_engine(
        #  app.config['SLAVE_SQLALCHEMY_DATABASE_URI'],
        #  pool_size = app.config.get('SQLALCHEMY_POOL_SIZE'),
        #  max_overflow = app.config['SQLALCHEMY_MAX_OVERFLOW'],
        #  pool_recycle = app.config['SQLALCHEMY_POOL_RECYCLE'],
        #  #  isolation_level = 'AUTOCOMMIT',
        #  #  isolation_level = 'READ UNCOMMITTED',
        #  echo=app.config.get("SQLALCHEMY_ECHO") or False
    #  )
    #  #  Session = sessionmaker(bind=engine)
    #  #  session = Session()

    #  session = scoped_session(
        #  sessionmaker(
            #  bind=engine,
            #  autoflush = False,
            #  autocommit = True,
        #  )
    #  )
    #  return DB(session())
