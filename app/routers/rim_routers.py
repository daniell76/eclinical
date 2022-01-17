# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : rim_routers.py
    Time : 2021/08/24 09:43:00
    Author : xiaf
    Version : 1.0
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_common_models import DbProjectRecord, DbEnvSummaryRecord, DbRimSummaryRecords, DbPriceResult, \
    DbDetailRecord, DbResourcePrice
from app.models.data_common_models import ProjectSummary, RecalculateParams
from app.models.data_rim_models import RimCostOut, RimSpecIn
from app.controllers.rim_controller import RimCalculator
from util.common import OsType, Currency, OriginAzureRegion, CalyxApp

router = APIRouter()

logger = logging.getLogger('fastapi')


@router.get("/projects/count")
async def get_rim_project_count(
        create_username: Optional[str] = None,
        request: Request = None,
        db: Session = Depends(get_db)):
    """
    get the total count of the projects
    :param create_username:
    :param request:
    :param db:
    :return:
    """
    localVars = locals()
    params = {"app": CalyxApp.RIM.value}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    count = DbProjectRecord.count_all(db, filter_by=params)
    return {"count": count}


@router.get("/projects", response_model=List[ProjectSummary])
async def get_rim_projects(
        create_username: Optional[str] = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 100,
        request: Request = None,
        db: Session = Depends(get_db)):
    """
    get project summary lists
    :param create_username:
    :param page_num:
    :param page_size:
    :param request:
    :param db:
    :return:
    """
    if Request is None:
        return
    localVars = locals()
    params = {"app": CalyxApp.RIM.value}
    for k in set(request.query_params.keys()).intersection(locals().keys()):
        params[k] = eval(k)
    params.pop("page_num", None)
    params.pop("page_size", None)
    logger.info(f"Get into DbProjectRecord.get_all(), username={create_username}")
    ret = DbProjectRecord.get_all(db, filter_by=params, page_num=page_num, page_size=page_size, reverse=True)
    return ret


@router.get("/projects/{project_id}/title", tags=["rim"], response_model=ProjectSummary)
async def get_rim_project_title_by_uuid(
        project_id: str,
        db: Session = Depends(get_db)):
    """
    get project summary entry by project ID
    :param project_id:
    :param db:
    :return:
    """
    return DbProjectRecord.get_by_project_id(db, project_id)


@router.get("/project/{project_id}/versions", tags=["rim"])
async def get_project_versions(project_id: str, db: Session = Depends(get_db)):
    """
    get the list of available version numbers of a given project
    :param project_id:
    :param db:
    :return:
    """
    return DbEnvSummaryRecord.get_versions(db, project_id)


@router.get("/project/{project_id}", tags=["rim"], response_model=RimCostOut)
async def get_project_by_uuid(project_id: str, request: Request, version: int = 0, detail: bool = True,
                              db: Session = Depends(get_db)):
    """
    Read from the DB.
    Load price calculation results of a give project with given version.
    If version not specified, load the latest version
    :param project_id:
    :param request:
    :param version: optional, if version not specified, get the latest version
    :param detail: whether to load detail BOM lists
    :param db:
    :return:
    """
    logger.info(f"calling get_project_by_uuid(project_id={project_id},version={version},detail={detail})")
    rim_calc = RimCalculator(user=request.state.user.username, db=db)
    rim_calc.set_proj_id(project_id)
    if version > 0:
        rim_calc.set_proj_version(version)
    else:
        rim_calc.refresh_proj_version()
    rim_calc.load_db_proj_record()
    rim_calc.load_db_env_records()
    rim_calc.load_db_proj_summary()
    if detail:
        rim_calc.load_db_detail_records()
    rim_calc.load_api_summary_out(detail)

    return rim_calc.summaryResultOut


@router.get("/project/{project_id}/spec", tags=["rim"], response_model=RimSpecIn)
async def get_project_spec_by_uuid(project_id: str, version: int = 0, db: Session = Depends(get_db)):
    """
    Read the RIM Spec from DB
    :param project_id: the uuid assigned to the project
    :param version: if <=0, get the latest version
    :param db: DB session
    :return: RIM Customer Spec
    """
    if version <= 0:
        version = DbEnvSummaryRecord.get_max_version(db, project_id)
    dbProj = DbProjectRecord.get_by_project_id(db, project_id)
    dbSum = DbRimSummaryRecords.get_by_project_id_version(db, project_id, version)
    rimSpec = RimCalculator.db_rim_summary_records_to_spec_in(dbSum)
    rimSpec.project.customer_name = dbProj.customer_name
    rimSpec.project.project_name = dbProj.project_name
    return rimSpec


@router.post("/project/new_project", tags=["rim"], response_model=RimCostOut)
async def create_project(rim_spec_in: RimSpecIn, request: Request, db: Session = Depends(get_db)):
    """
    Create a project from scratch, this includes
        a. calculate the T-Shirt size based on rim_spec_in
        b. according to the T-Shirt size, create a project headline entry in table 'project_records' (DbProjectRecord)
        c. create the initial version of each environment
    :param rim_spec_in: all the parameters in json format from frontend UI
    :param request: the HTTP request object (maybe redundant to rim_spec_in)
    :param db: database session
    :return: RimCostOut
    """
    # print(f'rim_spec_in is {rim_spec_in}')
    # print(f'request.body is {request.body}')
    rim_calc = RimCalculator(user=request.state.user.username, db=db, spec_in=rim_spec_in)
    rim_calc.new_proj()
    rim_calc.gen_api_summary_out()
    # save to db
    rim_calc.create_db_proj()
    rim_calc.create_db_proj_version()
    return rim_calc.summaryResultOut


@router.post("/project/{project_id}/calculate", tags=["rim"], response_model=RimCostOut)
async def calculate_project_version(project_id: str, rec_param: RecalculateParams, request: Request, db: Session = Depends(get_db)):
    """
    Calculate or recalculate a version.
    At least the spec must already in the database
    :param project_id:
    :param rec_param:
    :param request:
    :param db:
    :return:
    """
    if rec_param.version <= 0:
        version = DbEnvSummaryRecord.get_max_version(db, project_id)
    else:
        version = rec_param.version
    assert version > 0
    # create RIM calculator
    rim_calc = RimCalculator(user=request.state.user.username, db=db)
    rim_calc.load_db_proj_record(proj_id=project_id, version=version)
    rim_calc.set_original_owner(rim_calc.dbProjRecord.create_username, rim_calc.dbProjRecord.create_date)
    # spec must already in the DB. Load it
    rim_calc.load_db_proj_summary()
    if rec_param.recreate_bom:
        # delete the existing version
        DbEnvSummaryRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
        DbPriceResult.delete_by_project_version(db=db, uuid=project_id, version=version)
        DbDetailRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
        # rim_calc.specIn = rim_calc.db_rim_summary_records_to_spec_in(rim_calc.dbSummaryRecords)
        # print(rim_spec_in.json())
        # recalculate the version based on spec
        rim_calc.new_proj_version(version=version)
        rim_calc.gen_api_summary_out(rec_param.detail)
        # save it to db
        if rim_calc.dbSummaryRecords.is_customized:
            # if it was customized before, clear that flag
            DbRimSummaryRecords.update_by_id(db=db, row_id=rim_calc.dbSummaryRecords.id, is_customized=False)
        rim_calc.create_db_proj_version()
    else:
        # calculate based on existing BOM
        rim_calc.load_db_env_records()
        rim_calc.load_db_detail_records()
        rim_calc.gen_api_summary_out(rec_param.detail)
        rim_calc.update_db_proj_version_result()

    return rim_calc.summaryResultOut


@router.put("/project/{project_id}/{version}", tags=["rim"], response_model=RimCostOut)
async def update_project_version(project_id: str, version: int, rim_spec_in: RimSpecIn, request: Request,
                                 db: Session = Depends(get_db)):
    """
    Update an existing version of a given project.
    :param project_id:
    :param version:
    :param rim_spec_in:
    :param request:
    :param db:
    :return:
    """
    # Record the version creator's info
    recs = DbEnvSummaryRecord.get_by_project_version(db=db, uuid=project_id, version=version)
    if len(recs) > 0:
        create_username = recs[0].create_username
        create_date = recs[0].create_date
    else:
        create_username = None
        create_date = None
    # delete the old version content
    DbEnvSummaryRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbRimSummaryRecords.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbPriceResult.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbDetailRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
    # create new version content
    rim_calc = RimCalculator(user=request.state.user.username, db=db, spec_in=rim_spec_in)
    rim_calc.load_db_proj_record(proj_id=project_id, version=version)
    rim_calc.set_original_owner(create_username, create_date)
    rim_calc.dbSummaryRecords = rim_calc.new_db_proj_summary()
    rim_calc.get_tshirt_size()
    rim_calc.new_version_content()
    rim_calc.gen_api_summary_out()
    # save to db
    rim_calc.create_db_proj_version()
    return rim_calc.summaryResultOut


@router.post("/project/{project_id}/new_version", tags=["rim"], response_model=RimCostOut)
async def create_project_version(project_id: str, rim_spec_in: RimSpecIn, request: Request, db: Session = Depends(get_db)):
    """
    Create a new version of a given project.
    :param project_id:
    :param rim_spec_in:
    :param request:
    :param db:
    :return:
    """
    rim_calc = RimCalculator(user=request.state.user.username, db=db, spec_in=rim_spec_in)
    rim_calc.set_proj_id(project_id)
    rim_calc.load_db_proj_record()
    rim_calc.new_proj_version_number()
    rim_calc.dbSummaryRecords = rim_calc.new_db_proj_summary()
    rim_calc.get_tshirt_size()
    rim_calc.new_version_content()
    rim_calc.gen_api_summary_out()
    # save to db
    rim_calc.create_db_proj_version()
    return rim_calc.summaryResultOut


@router.put("/project/{project_id}", tags=["rim"], response_model=ProjectSummary)
async def update_project_summary(proj_sum: ProjectSummary, request: Request, db: Session = Depends(get_db)):
    """
    Update project summaries
    :param proj_sum:
    :param request:
    :param db:
    :return:
    """
    db.query(DbProjectRecord).filter(DbProjectRecord.uuid == proj_sum.uuid).update({
        "customer_name": proj_sum.customer_name,
        "project_name": proj_sum.project_name,
        "remark": proj_sum.remark,
        "update_username": proj_sum.update_username
    })
    db.commit()
    return DbProjectRecord.get_by_project_id(db, proj_sum.uuid)


@router.delete("/project/{project_id}/{version}", tags=["rim"])
async def delete_project_version(project_id: str, version: int, db: Session = Depends(get_db)):
    """
    Delete a specific version of a project, including version spec and results
    This will affect the following DB tables:
        env_summary_records, rim_summary_records, project_price_results, detail_records
    If all versions of a project are deleted, the project will be deleted as well
    :param project_id:
    :param version:
    :param db:
    :return:
    """
    DbEnvSummaryRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbRimSummaryRecords.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbPriceResult.delete_by_project_version(db=db, uuid=project_id, version=version)
    DbDetailRecord.delete_by_project_version(db=db, uuid=project_id, version=version)
    # delete from project_records if all versions are deleted
    db_env = DbEnvSummaryRecord.get_by_project_id(db, project_id)
    if not db_env:
        DbProjectRecord.delete_by_project_id(db=db, uuid=project_id)
    db.commit()
    return {}


@router.delete("/project/{project_id}", tags=["rim"])
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    Completely delete a project data with give project_id, including all versions with all results.
    This will affect the following DB tables:
        project_records, env_summary_records, rim_summary_records, project_price_results, detail_records
    :param project_id:
    :param db:
    :return:
    """
    DbProjectRecord.delete_by_project_id(db=db, uuid=project_id)
    DbEnvSummaryRecord.delete_by_project_id(db=db, uuid=project_id)
    DbRimSummaryRecords.delete_by_project_id(db=db, uuid=project_id)
    DbPriceResult.delete_by_project_id(db=db, uuid=project_id)
    DbDetailRecord.delete_by_project_id(db=db, uuid=project_id)
    db.commit()
    return {}
