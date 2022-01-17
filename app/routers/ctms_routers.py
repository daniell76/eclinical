# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : ctms_routers.py
    Time : 2021/08/24 09:33:00
    Author : xiaf
    Version : 1.0
"""

from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()

logger = logging.getLogger('fastapi')


@router.get("/")
async def read_records():
    logger.info("Get into read_items()")
    return [{"name": "Item Foo"}, {"name": "item Bar"}]


@router.get("/{record_id}")
async def read_item(record_id: str):
    logger.info(f"Get into read_item({record_id})")
    return {"name": "Fake Specific Item", "record_id": record_id}


@router.put(
    "/{record_id}",
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(record_id: str):
    if record_id != "foo":
        raise HTTPException(status_code=403, detail="You can only update the item: foo")
    return {"record_id": record_id, "name": "The Fighters"}
