# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : data_common_models.py
    Time : 2021/08/24 16:25:00
    Author : xiaf
    Version : 1.0
"""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.util.common import BillingType, BomType, Currency, OsType, OriginAzureRegion, CalyxApp
# from app.models.db_common_models import DbResourcePrice


########################################
# API Output Models
########################################
class ProjectSummary(BaseModel):
    """project headline"""
    id: Optional[int]
    uuid: Optional[str] = None
    app: Optional[CalyxApp] = CalyxApp.RIM
    customer_name: Optional[str] = None
    project_name: Optional[str] = None
    remark: Optional[str] = None
    create_username: Optional[str] = None
    update_username: Optional[str] = None
    create_date: Optional[datetime] = datetime.now()  # default is today's date
    update_date: datetime = datetime.now()

    class Config:
        orm_mode = True


class _DetailCosts(BaseModel):
    id: Optional[int]
    sku: str = None
    vendor: str = None
    display_name: str = None
    app_role: str = None
    qty: int = None
    currency: Currency = None
    unit_price: float = None  # annual price/oneoff price
    total_price: float = None  # unit_price * qty
    sum_total_price: Optional[float]  # for compound items
    bom_type: BomType = None
    bom_subtype: str = None
    billing_type: BillingType = None  # annual cost or one off cost
    service: Optional[str]  # Azure service name
    region: Optional[str]  # Azure region
    os_type: Optional[str]  # only for VM, Windows/RHEL/CENTOS
    vcpu: Optional[int]  # only for VM
    memory: Optional[float]  # only for VM, unit: GB
    disk_size: Optional[int]  # only for Storage, unit: GB
    # components: Optional[List]  # List of components DetailCosts


class DetailCosts(_DetailCosts):
    components: Optional[List[_DetailCosts]]  # List of components DetailCosts


class ResourcePrice(BaseModel):
    id: Optional[int] = None
    vendor: str
    service_name: Optional[str] = None
    description: Optional[str] = None
    sku: str
    os_type: Optional[OsType] = None
    currency: Currency = Currency.USD
    billing_type: Optional[BillingType] = BillingType.ANNUAL
    unit_price: float = 0
    reservation_term: Optional[int] = 0
    azure_region: Optional[OriginAzureRegion] = None
    create_username: Optional[str] = None
    update_username: Optional[str] = None
    create_date: Optional[datetime] = datetime.now()
    update_date: datetime = datetime.now()

    class Config:
        orm_mode = True


########################################
# API Input Models
########################################
class RecalculateParams(BaseModel):
    version: Optional[int] = 0
    recreate_bom: Optional[bool] = False
    detail: Optional[bool] = False

    class Config:
        orm_mode = True
