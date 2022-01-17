# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : common.py
    Time : 2021/08/20 17:53:23
    Author : xiaf
    Version : 1.0
"""

from fastapi.responses import JSONResponse
from enum import Enum


class UserRole(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class AzureRegion(Enum):
    EU = {"primary": "EU WEST", "secondary": "EU NORTH"}
    US = {"primary": "US EAST 2", "secondary": "US CENTRAL"}
    CN = {"primary": "CN EAST 2", "secondary": "CN NORTH 2"}


class OriginAzureRegion(Enum):
    EU_WEST = "EU WEST"
    EU_NORTH = "EU NORTH"
    US_EAST_2 = "US EAST 2"
    US_CENTRAL = "US CENTRAL"
    CN_EAST_2 = "CN EAST 2"
    CN_NORTH_2 = "CN NORTH 2"


class TeeShirtSize(Enum):
    XSMALL = "XSMALL"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    XLARGE = "XLARGE"


class OsType(str, Enum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"


class CalyxRegion(str, Enum):
    EU = "EU"
    US = "US"
    CN = "CN"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CNY = "CNY"


# class ExchangeRate(float, Enum):
#     USD = 1
#     EUR = 1.15
#     GBP = 1.3
#     CNY = 0.15


class CalyxEnv(str, Enum):
    SHARED = 'SHARED'
    PROD = 'PROD'
    NONPRODVAL = 'NONPRODVAL'
    NONPROD = 'NONPROD'


class BomType(str, Enum):
    LABOR = 'LABOR'
    INFRA = 'INFRA'
    LICENSE = 'LICENSE'
    SUPPORT = 'SUPPORT'


class BomLevel(str, Enum):
    PRIMARY = 'PRIMARY'
    SECONDARY = 'SECONDARY'


class BillingType(str, Enum):
    ANNUAL = 'ANNUAL'
    ONEOFF = 'ONEOFF'


class ServerBackupType(str, Enum):
    APP = 'APP'
    DB = 'DB'
    FILE = 'FILE'


class ServerBackupAction(str, Enum):
    FIRST_DEDUPE = 'FIRST_DEDUPE'
    FIRST_COMPRESS = 'FIRST_COMPRESS'
    ONGOING_DEDUPE = 'ONGOING_DEDUPE'
    ONGOING_COMPRESS = 'ONGOING_COMPRESS'


class CalyxApp(str, Enum):
    RIM = 'RIM'
    CTMS = 'CTMS'


class LinuxDist(str, Enum):
    RHEL = 'RHEL'
    CENTOS = 'CENTOS'


def trueReturn(data, msg):
    """ 操作成功结果 """
    result = {
        "status": True,
        "data": data,
        "msg": msg
    }
    return JSONResponse(content=result)


def falseReturn(data, msg):
    """ 操作成功结果 """
    result = {
        "status": False,
        "data": data,
        "msg": msg
    }
    return JSONResponse(content=result)


def trueContent(data, msg):
    """ 操作成功结果 """
    result = {
        "status": True,
        "data": data,
        "msg": msg
    }
    return result


def falseContent(data, msg):
    """ 操作成功结果 """
    result = {
        "status": False,
        "data": data,
        "msg": msg
    }
    return result
