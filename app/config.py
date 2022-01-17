# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    Filename: config.py
    Description: config.py

    Created by xiaf at 2021-08-20 15:00:00
"""

import os


class Config:

    SITE_NAME = u'Calyx App Dimensioning Tool'

    # Consider SQLALCHEMY_COMMIT_ON_TEARDOWN harmful
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SQLALCHEMY_POOL_RECYCLE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # to get a string like this run:
    # openssl rand -hex 32
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"

    # SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


class DevelopmentConfig(Config):

    DEBUG = True

    SQLALCHEMY_ECHO = False

    MYSQL_USER = 'calyx'
    MYSQL_PASS = 'calyx'
    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = '3306'
    MYSQL_DB = 'calyx'

    SQLALCHEMY_DATABASE_URI = f'''mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'''


class ProductionConfig(Config):

    DEBUG = True

    # mysql configuration
    MYSQL_USER = 'calyx'
    MYSQL_PASS = 'calyx'
    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = '3306'
    MYSQL_DB = 'calyx'

    if len(MYSQL_USER) & len(MYSQL_PASS) & len(MYSQL_HOST) & len(MYSQL_PORT) & len(MYSQL_DB):
        SQLALCHEMY_DATABASE_URI = f'''mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'''


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}


def get_config():
    config_name = os.getenv('FASTAPI_ENV') or 'default'
    return config[config_name]
