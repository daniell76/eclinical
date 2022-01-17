# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2018-2019 TEST
    All rights reserved

    File : items.py
    Time : 2020/07/27 14:32:51
    Author : mazhiyong
    Version : 1.0
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_models import User, DBUser
from app.models.data_common_models import ResourcePrice
from app.models.db_common_models import DbResourcePrice
from app.util.common import Currency, OriginAzureRegion, OsType
import logging

router = APIRouter()

logger = logging.getLogger('fastapi')


@router.get("/users/count")
async def get_user_count(
        username: Optional[str] = None,
        role: Optional[str] = None,
        active: Optional[int] = None,
        request: Request = None,
        db: Session = Depends(get_db)):
    localVars = locals()
    params = {}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    if len(params) <= 0:
        params = None
    count = DBUser.count_all(db, filter_by=params)
    return {"count": count}


@router.get("/users", response_model=List[User], response_model_exclude_unset=True)
async def get_all_users(
        username: Optional[str] = None,
        role: Optional[str] = None,
        active: Optional[int] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 100,
        request: Request = None,
        db: Session = Depends(get_db)):
    logger.info("Get into users()")
    localVars = locals()
    # print(localVars)
    # print(request.query_params.keys())
    params = {}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    params.pop("page_num", None)
    params.pop("page_size", None)
    if len(params) <= 0:
        params = None
    print(params)
    ret = DBUser.get_all(db, filter_by=params, page_num=page_num, page_size=page_size)
    return ret


@router.get("/resources/count")
async def get_resource_count(
        id: Optional[int] = None,
        vendor: Optional[str] = None,
        service_name: Optional[str] = None,
        sku: Optional[str] = None,
        os_type: Optional[OsType] = None,
        currency: Optional[Currency] = None,
        unit_price: Optional[float] = None,
        reservation_term: Optional[int] = None,
        azure_region: Optional[OriginAzureRegion] = None,
        request: Request = None,
        db: Session = Depends(get_db)):
    localVars = locals()
    params = {}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    if "azure_region" in params.keys():
        params["azure_region"] = params["azure_region"].value
    if len(params) <= 0:
        params = None
    count = DbResourcePrice.count_all(db, filter_by=params)
    return {"count": count}


@router.get("/resources", response_model=List[ResourcePrice], response_model_exclude_unset=True)
# @router.get("/resources")
async def get_resources(
        id: Optional[int] = None,
        vendor: Optional[str] = None,
        service_name: Optional[str] = None,
        sku: Optional[str] = None,
        os_type: Optional[OsType] = None,
        currency: Optional[Currency] = None,
        unit_price: Optional[float] = None,
        reservation_term: Optional[int] = None,
        azure_region: Optional[OriginAzureRegion] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 100,
        request: Request = None,
        db: Session = Depends(get_db)):
    logger.info("Get into resources()")
    localVars = locals()
    # print(localVars)
    # print(request.query_params.keys())
    params = {}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    params.pop("page_num", None)
    params.pop("page_size", None)
    if "azure_region" in params.keys():
        params["azure_region"] = params["azure_region"].value
    if len(params) <= 0:
        params = None
    print(params)
    ret = DbResourcePrice.get_all(db, filter_by=params, page_num=page_num, page_size=page_size)
    # Sanity check on Enum data
    for x in ret:
        if len(x.os_type) == 0:
            x.os_type = None
        if len(x.azure_region) == 0:
            x.azure_region = None
        if len(x.currency) == 0:
            x.currency = "USD"
    return ret


@router.get("/resource/{item_id}")
async def get_resource(item_id: str):
    logger.info(f"Get into read_item({item_id})")
    return {"name": "Fake Specific Item", "item_id": item_id}


@router.put(
    "/resource/{item_id}",
    responses={403: {"description": "Operation forbidden"}},
)
async def update_resource(item_id: str):
    if item_id != "foo":
        raise HTTPException(status_code=403, detail="You can only update the item: foo")
    return {"item_id": item_id, "name": "The Fighters"}
