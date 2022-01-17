from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.sql.functions import func
from fastapi import Depends
from app.database import get_db
from app.models.db_common_models import DbProjectRecord


async def _get_project_count(
        create_username: str = None,
        update_username: str = None,
        app_name: str = None,
        db: Session = Depends(get_db)) -> int:
    if app_name is None:
        return 0
    if create_username is not None and update_username is not None:
        count = db.query(func.count(DbProjectRecord.id)).filter(
            app_name == app_name,
            or_(create_username == create_username, update_username == update_username)
            ).scalar()
        return count
    cond = {'app_name': app_name}
    if create_username is None:
        cond['create_username'] = create_username
    if update_username is None:
        cond['update_username'] = update_username
    return DbProjectRecord.count_all(db, {app_name: app_name})


async def _get_projects(
        create_username: str = None,
        update_username: str = None,
        app_name: str = None,
        page_num: Optional[int] = 1,
        page_size: Optional[int] = 100,
        db: Session = Depends(get_db)
        ) -> List[DbProjectRecord]:
    if app_name is None:
        return []
    offset = page_size * (page_num - 1)
    if create_username is not None and update_username is not None:
        data = db.query(DbProjectRecord).filter(
            app_name == app_name,
            or_(create_username == create_username, update_username == update_username)
            ).limit(page_size).offset(offset).all()
    else:
        cond = {'app_name': app_name}
        if create_username is None:
            cond['create_username'] = create_username
        if update_username is None:
            cond['update_username'] = update_username
        data = DbProjectRecord.get_all(db, filter_by=cond, page_num=page_num, page_size=page_size)
    return [x for x in data]