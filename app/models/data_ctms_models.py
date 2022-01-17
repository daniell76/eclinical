# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : data_ctms_models.py
    Time : 2021/09/06 13:52:40
    Author : xiaf
    Version : 1.0
"""

from datetime import datetime
from pydantic import BaseModel
from util.common import CalyxRegion


########################################
# CTMS calculation input parameters
########################################
class CtmsInProjectInfo(BaseModel):
    """Input Parameters"""
    customer_name: str = "Unknown Customer"
    project_name: str = "Unknown Project"
    discount: float = 0  # overall discount we give to the customer
    author: str = "Unknown User"  # user created this record
    date: datetime = datetime.now()  # default is today's date
    version: int = 1  # version of the project
    is_customized: bool = False  # whether this estimation been customized, e.g. price changed, add/remove bom


class CtmsInUserInfo(BaseModel):
    totalUsers: int = 0  # Total number of users
    concurrentUserRatio: float = 0.1  # default 10% of concurrent users


class CtmsInEnvInfo(BaseModel):
    nProdEnv: int = 1  # number of production environment
    nNonProdValidatedEnv: int = 1  # number of non-production validated environment
    nNonProdEnv: int = 1  # number of non-production environment
    prodEnvSharedRatio: float = 1  # 100%
    nonProdValidatedEnvSharedRatio: float = 1  # 100%
    nonProdEnvSharedRatio: float = 1  # 100%


class CtmsInMiscInfo(BaseModel):
    isMultiTenant: bool = True
    multiTenantDbRatio: float = 0.0625  # A tenant uses 6.25% of the DB
    hasProdReadReplicaDatabase: bool = False
    hasNonProdValReadReplicaDatabase: bool = False
    hasNonProdReadReplicaDatabase: bool = False
    dbStorage: int = 512  # Oracle DB VM storage size (GB/Vm)
    azureRegion: CalyxRegion = CalyxRegion.CN
    contractTerm: int = 3  # years


class CtmsInAnalyticsInfo(BaseModel):
    # Style Report options
    hasStyleReport: bool = True
    # PowerBI options
    hasPowerBi: bool = False
    reportCreators: int = 0
    superUsers: int = 0
    standardUser: int = 0


class CtmsInInternalInfo(BaseModel):
    # The following parameters most of the time will not change
    useAzureRiRate: bool = True  # use RI/CPP rate
    hasVendorDiscount: bool = True  # Vendor pre-agreed discounts included (e.g. Oracle)
    slaTarget: float = 0.995  # 99.5% Availability
    hasDisasterRecovery: bool = True  # has DR design
    drRpo: int = 1  # 1 hour RPO
    drRto: int = 8  # 8 hour RTO


class CtmsSpecIn(BaseModel):
    project: CtmsInProjectInfo = CtmsInProjectInfo()
    users: CtmsInUserInfo = CtmsInUserInfo()
    environments: CtmsInEnvInfo = CtmsInEnvInfo()
    misc: CtmsInMiscInfo = CtmsInMiscInfo()
    analytics: CtmsInAnalyticsInfo = CtmsInAnalyticsInfo()
    internal: CtmsInInternalInfo = CtmsInInternalInfo()


