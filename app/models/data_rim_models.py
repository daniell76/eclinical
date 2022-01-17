# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : data_rim_models.py
    Time : 2021/08/24 15:17:40
    Author : xiaf
    Version : 1.0
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

from models.data_common_models import DetailCosts
from util.common import CalyxRegion, TeeShirtSize


########################################
# RIM calculation input parameters
########################################
class RimInProjectInfo(BaseModel):
    """Input Parameters"""
    customer_name: Optional[str] = "Unknown Customer"
    project_name: Optional[str] = "Unknown Project"
    discount: Optional[float] = 0  # overall discount we give to the customer
    author: Optional[str] = "Unknown User"  # user created this record
    date: Optional[datetime] = datetime.now()  # default is today's date
    version: Optional[int] = 1  # version of the project
    is_customized: Optional[bool] = False  # whether this estimation been customized, e.g. price changed, add/remove bom


class RimInUserInfo(BaseModel):
    totalRegistrationUsers: Optional[int] = 0  # Total Registration Users
    concurrentRegistrationUsers: Optional[int] = 0  # Concurrent Registration Users, not used as of now
    totalPublishUsers: Optional[int] = 0  # Total Publish Users
    concurrentPublishUsers: Optional[int] = 0  # Concurrent Publish Users
    totalViewUsers: Optional[int] = 0  # Total View Users
    concurrentViewUsers: Optional[int] = 0  # Concurrent View Users, not used as of now


class RimInEnvInfo(BaseModel):
    nProdEnv: Optional[int] = 1  # number of production environment
    nNonProdValidatedEnv: Optional[int] = 0  # number of non-production validated environment
    nNonProdEnv: Optional[int] = 0  # number of non-production environment
    prodEnvSharedRatio: Optional[float] = 1  # 100%
    nonProdValidatedEnvSharedRatio: Optional[float] = 1  # 100%
    nonProdEnvSharedRatio: Optional[float] = 1  # 100%


class RimInMiscInfo(BaseModel):
    isMultiTenant: Optional[bool] = True
    multiTenantDbRatio: Optional[float] = 0.0625  # A tenant uses 6.25% of the DB
    hasProdReadReplicaDatabase: Optional[bool] = True
    hasNonProdValReadReplicaDatabase: Optional[bool] = True
    hasNonProdReadReplicaDatabase: Optional[bool] = True
    hasCitrix: Optional[bool] = True
    dbStorage: Optional[int] = 512  # Oracle DB VM storage size (GB/Vm)
    azureRegion: Optional[CalyxRegion] = CalyxRegion.CN
    contractTerm: Optional[int] = 3  # years


class RimInAnalyticsInfo(BaseModel):
    # Analytics
    hasPowerBi: Optional[bool] = False
    reportCreators: Optional[int] = 0
    superUsers: Optional[int] = 0
    standardUser: Optional[int] = 0


class RimInFileShareInfo(BaseModel):
    # Azure file share
    azureFileShareStorage: Optional[int] = 0  # unit: GB, 0 means not used
    azureFilesShareSyncServers: Optional[int] = 1  # == 1 server: Option 2, > 1 server, option 3


class RimInInternalInfo(BaseModel):
    # The following parameters most of the time will not change
    useAzureRiRate: Optional[bool] = True  # use RI/CPP rate
    hasVendorDiscount: Optional[bool] = True  # Vendor pre-agreed discounts included (e.g. Oracle)
    slaTarget: Optional[float] = 0.995  # 99.5% Availability
    hasDisasterRecovery: Optional[bool] = True  # has DR design
    drRpo: Optional[int] = 1  # 1 hour RPO
    drRto: Optional[int] = 8  # 8 hour RTO


class RimSpecIn(BaseModel):
    project: RimInProjectInfo = RimInProjectInfo()
    users: RimInUserInfo = RimInUserInfo()
    environments: RimInEnvInfo = RimInEnvInfo()
    misc: RimInMiscInfo = RimInMiscInfo()
    analytics: RimInAnalyticsInfo = RimInAnalyticsInfo()
    azureFileShare: RimInFileShareInfo = RimInFileShareInfo()
    internal: Optional[RimInInternalInfo] = RimInInternalInfo()


########################################
# RIM API Results
########################################
class RimOutProjectInfo(BaseModel):
    """RIM Results: project headline"""
    projId: str = "Unknown Project ID"
    customerName: str = "Unknown Customer"
    projName: str = "Unknown Project Name"
    remark: str = ""
    version: int = 1
    createdBy: str = "Unknown User"
    date: datetime = datetime.now()  # default is today's date


class RimOutDetailRunningCost(BaseModel):
    """RIM Results: yearly summary running cost by components"""
    azureServers: float = 0
    azureSharedServices: float = 0
    serverSoftwareLicensing: float = 0
    backupServices: float = 0
    databaseLicensing: float = 0
    azureNetworkServices: float = 0
    clientSoftwareLicensing: float = 0
    azurePowerBi: float = 0
    azureFileShare: float = 0
    managedServices: float = 0
    total: float = 0


class RimOutSummaryRunningCost(BaseModel):
    """RIM Results: yearly summary running cost by sales categories"""
    labor: float = 0
    infra: float = 0
    licenses: float = 0
    total: float = 0


class RimOutOneOffCost(BaseModel):
    """RIM Results: one off cost and 5 years CAPEX"""
    initSetup: float = 0
    capex: float = 0  # only for Calyx internal financial use


class RimOutMisc(BaseModel):
    tshirt_size: Optional[TeeShirtSize]


class RimCostOut(BaseModel):
    """RIM Results: Aggregation class"""
    projInfo: RimOutProjectInfo = RimOutProjectInfo()
    yearlyDetailCost: RimOutDetailRunningCost = RimOutDetailRunningCost()
    yearlySummaryCost: RimOutSummaryRunningCost = RimOutSummaryRunningCost()
    oneOffCost: Optional[RimOutOneOffCost]
    misc: Optional[RimOutMisc]
    details: Optional[List[DetailCosts]]


