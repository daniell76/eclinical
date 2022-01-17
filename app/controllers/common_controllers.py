# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : rim_routers.py
    Time : 2021/08/27 22:43:00
    Author : xiaf
    Version : 1.0
"""
import math
import re
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.db_common_models import DbAzureDiskSpec, DbAzureVmSpec, DbBackupRatio, DbDetailRecord, \
    DbEnvSummaryRecord, DbExchangeRate, DbProjectRecord, DbResourcePrice, DbRimSummaryRecords, DimensionTemplate
from app.models.data_common_models import DetailCosts
from app.models.data_ctms_models import CtmsSpecIn
from app.models.data_rim_models import RimCostOut, RimSpecIn
from util.common import AzureRegion, BillingType, BomLevel, BomType, CalyxApp, CalyxEnv, Currency, TeeShirtSize


class AppCalculator:

    def __init__(self, user: str, db: Session, spec_in: Union[RimSpecIn, CtmsSpecIn] = None,
                 proj_id: str = None, version: int = 0):
        self.user: str = user
        self.db: Session = db
        self.specIn: Union[RimSpecIn, CtmsSpecIn] = spec_in
        self.summaryResultOut: Optional[Union[RimCostOut]] = None
        self.detailResultOut: Optional[List[DetailCosts]] = None
        self.projId: str = proj_id
        self.version: int = version
        self.dbProjRecord: Optional[DbProjectRecord] = None
        self.dbEnvRecords: Dict[CalyxEnv, DbEnvSummaryRecord] = {}
        self.dbDetailRecords: Dict[CalyxEnv, List[DbDetailRecord]] = {}
        self.dbSummaryRecords: Optional[Union[DbRimSummaryRecords]] = None
        # load backup ratio table
        self.dbBackupRatioDict = DbBackupRatio.get_backup_ratio_dict(self.db)
        # load Azure VM spec table
        self.dbAzureVmSpecDict = DbAzureVmSpec.get_vm_spec_dict(self.db)
        # load Azure disk spec table
        self.dbAzureDiskSpecDict = DbAzureDiskSpec.get_disk_spec_dict(self.db)
        # load exchange rate
        self.dbExchangeRateDict = DbExchangeRate.get_exchange_rate_dict(self.db)
        # place holder for templates
        self.templates: Dict[CalyxEnv, List[DimensionTemplate]] = {}
        # place holder for capex
        self.capex = 0
        # place holder for T-Shirt Size
        self.tshirt_size: Optional[TeeShirtSize] = None
        # in case we are updating a version, record the original author and create time
        self.original_author = None
        self.original_create_time = None

    def set_original_owner(self, author: str, created_on: datetime):
        self.original_author = author
        self.original_create_time = created_on

    def set_proj_id(self, proj_id: str):
        self.projId = proj_id

    def set_proj_version(self, version: int):
        self.version = version

    def refresh_proj_version(self):
        """
        If project ID is not None, then set the self.version to the max version number of that project
        :return:
        """
        if self.projId is None:
            return
        self.version = DbEnvSummaryRecord.get_max_version(self.db, self.projId)

    def new_db_proj_record(self) -> DbProjectRecord:
        """
        Create a new DB entry mapped to table 'project_records'
        create a new project id (uuid) for this project
        initialize the version number to 1
        This method is only called when create a brand new project.
        Do NOT call this method when update or add a new version to existing project
        :return:
        """
        while True:
            param = {
                "uuid": uuid.uuid4().hex,
                "customer_name": self.specIn.project.customer_name,
                "project_name": self.specIn.project.project_name,
                "create_username": self.user,
                "update_username": self.user
            }
            if not DbProjectRecord.get_by_project_id(self.db, param["uuid"]):
                # no record found, use this uuid
                break
        if self.original_author is not None:
            param["create_username"] = self.original_author
        if self.original_create_time is not None:
            param["create_date"] = self.original_create_time
        db_proj = DbProjectRecord(**param)
        return db_proj

    def load_db_proj_record(self, proj_id: str = None, version: int = None):
        """
        Load a given version of project DB entry
        If version is not given, load the latest version
        :param proj_id: must be a valid project ID
        :param version: version of the project, default to the latest version
        :return:
        """
        if proj_id is not None:
            self.projId = proj_id
        db_proj = DbProjectRecord.get_by_project_id(self.db, self.projId)
        if version is None:
            if self.version is None:
                self.refresh_proj_version()
        else:
            self.version = version
        self.dbProjRecord = db_proj

    def new_proj_version_number(self):
        """
        Find the max version number in DB, then plus 1
        self.projId must be a valid project ID
        :return:
        """
        self.refresh_proj_version()
        self.version += 1

    def new_db_env_records(self):
        """
        create DB entries for all types of environments
        :return: None
        """
        self.dbEnvRecords = {}
        for env_type in CalyxEnv:
            db_env = self.new_db_env_record(CalyxEnv(env_type))
            if db_env:
                self.dbEnvRecords[CalyxEnv(env_type)] = db_env

    def new_db_env_record(self, env_type: CalyxEnv) -> Optional[DbEnvSummaryRecord]:
        """
        Create a new DB entry mapped to table 'env_summary_records', under the current project
        self.projId must be set before make this call
        This method is called when create a new project or new version
        According to input parameter (self.specIn), if the quantity is greater than 0, create and return the DB entry,
        otherwise return None.
        :param env_type: PROD/NONPRODVAL/NONPROD/SHARED
        :return: DB entry or None
        """
        if self.projId is None:
            return
        if env_type is CalyxEnv.PROD:
            qty = self.specIn.environments.nProdEnv
            shared_ratio = self.specIn.environments.prodEnvSharedRatio
        elif env_type is CalyxEnv.NONPRODVAL:
            qty = self.specIn.environments.nNonProdValidatedEnv
            shared_ratio = self.specIn.environments.nonProdValidatedEnvSharedRatio
        elif env_type is CalyxEnv.NONPROD:
            qty = self.specIn.environments.nNonProdEnv
            shared_ratio = self.specIn.environments.nonProdEnvSharedRatio
        else:
            # There is always shared resources
            env_type = CalyxEnv.SHARED
            qty = 1
            shared_ratio = 1
        if qty < 1:
            return
        param = {
            "uuid": self.projId,
            "version": self.version,
            "env": env_type.value,
            "tshirt_size": self.tshirt_size.value,
            "qty": qty,
            "uptime_ratio": 1,  # deprecated
            "shared_ratio": shared_ratio,
            "create_username": self.user if self.original_author is None else self.original_author,
            "update_username": self.user,
            "create_date": self.original_create_time
        }
        db_env = DbEnvSummaryRecord(**param)
        return db_env

    def load_db_env_records(self):
        """
        load DB entries with given project id and version
        self.projId and self.version must be a valid value
        :return: None
        """
        self.dbEnvRecords = {}
        for env_type in CalyxEnv:
            db_env = self.get_db_env_record(CalyxEnv(env_type))
            if db_env:
                self.dbEnvRecords[CalyxEnv(env_type)] = db_env

    def get_db_env_record(self, env_type: CalyxEnv) -> DbEnvSummaryRecord:
        """
        read env summary records from DB
        self.projId and self.version must be a valid value
        :param env_type: SHARED, PROD, NONPRODVAL, or NONPROD
        :return: the DB record, or None if not found
        """
        db_env = DbEnvSummaryRecord.get_by_project_id_version_env(self.db, self.projId, self.version, env_type)
        return db_env

    def new_db_detail_record(self, env_type: CalyxEnv, **kwargs) -> Optional[DbDetailRecord]:
        """
        Create a BoM entry mapping to table 'detail_records', for a particular env within a project version.
        uuid + version + env is used to join with other tables
        :param env_type:
        :param kwargs:
        :return:
        """
        if self.projId is None:
            return
        param = {
            "uuid": self.projId,
            "version": self.version,
            "env": env_type,
            "create_username": self.user,
            "update_username": self.user
        }
        param = {**param, **kwargs}
        db_detail = DbDetailRecord(**param)
        return db_detail

    def load_db_detail_records(self):
        """
        read the DB detail records of each environment of a give project version
        self.dbEnvRecords must be loaded/created before make this call
        :return:
        """
        self.dbDetailRecords = {}
        for env in self.dbEnvRecords:
            self.dbDetailRecords[env] = DbDetailRecord.get_by_project_id_version_env(
                self.db, self.projId, self.version, env)

    def new_db_bom_from_price(self, db_rsc_price: DbResourcePrice, env_type: CalyxEnv, app_role: str, qty: int,
                              lv: BomLevel, bom_type: BomType, bom_subtype: str) -> Optional[DbDetailRecord]:
        """
        Create a BoM entry from a disk price entry
        :param db_rsc_price: the price entry of the resource
        :param env_type:
        :param app_role:
        :param qty:
        :param lv:
        :param bom_type:
        :param bom_subtype:
        :return:
        """
        if self.projId is None:
            return
        db_detail = self.new_db_detail_record(
            remark=db_rsc_price.description,
            env_type=env_type,
            vendor=db_rsc_price.vendor,
            sku=db_rsc_price.sku,
            qty=qty,
            app_role=app_role,
            lv=lv,
            bom_type=bom_type,
            bom_subtype=bom_subtype,
            resource_type=db_rsc_price.service_name,
            billing_type=BillingType(db_rsc_price.billing_type),
            unit_price=db_rsc_price.unit_price,
            total_price=db_rsc_price.unit_price * qty,
            currency=db_rsc_price.currency
        )
        return db_detail

    def new_db_bom_vm_from_price(self, db_rsc_price: DbResourcePrice, env_type: CalyxEnv, app_role: str,
                                 qty: int) -> Optional[DbDetailRecord]:
        """
        Create a primary BoM entry from a VM price object
        :param db_rsc_price: the price entry of the VM
        :param env_type:
        :param app_role:
        :param qty:
        :return:
        """
        if self.projId is None:
            return
        db_detail = self.new_db_detail_record(
            remark=db_rsc_price.description,
            env_type=env_type,
            vendor=db_rsc_price.vendor,
            sku=db_rsc_price.sku,
            qty=qty,
            app_role=app_role,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Azure Servers",
            resource_type=db_rsc_price.service_name,
            billing_type=BillingType(db_rsc_price.billing_type),
            unit_price=db_rsc_price.unit_price,
            total_price=db_rsc_price.unit_price * qty,
            currency=db_rsc_price.currency
        )
        return db_detail

    def new_db_bom_disk_from_price(self, db_rsc_price: DbResourcePrice, env_type: CalyxEnv, app_role: str, qty: int) \
            -> Optional[DbDetailRecord]:
        """
        Create a BoM entry from a disk price entry, as a secondary entry of a VM entry
        :param db_rsc_price: the price entry of the disk
        :param env_type:
        :param app_role:
        :param qty:
        :return:
        """
        if self.projId is None:
            return
        db_detail = self.new_db_detail_record(
            remark=db_rsc_price.description,
            env_type=env_type,
            vendor=db_rsc_price.vendor,
            sku=db_rsc_price.sku,
            qty=qty,
            app_role=app_role,
            lv=BomLevel.SECONDARY,
            bom_type=BomType.INFRA,
            bom_subtype="Azure Servers",
            resource_type=db_rsc_price.service_name,
            billing_type=BillingType(db_rsc_price.billing_type),
            unit_price=db_rsc_price.unit_price,
            total_price=db_rsc_price.unit_price,
            currency=db_rsc_price.currency
        )
        return db_detail

    def has_read_replica_db(self, env: CalyxEnv) -> bool:
        return (env == CalyxEnv.PROD and self.dbSummaryRecords.has_prod_read_replica_db) or \
            (env == CalyxEnv.NONPRODVAL and self.dbSummaryRecords.has_nonprodval_read_replica_db) or \
            (env == CalyxEnv.NONPROD and self.dbSummaryRecords.has_nonprod_read_replica_db)

    def get_vm_oracle_lic(self, vm_dim_temp: DimensionTemplate) -> Optional[DbDetailRecord]:
        """Get the oracle database license BoM entry of a azure VM"""
        # Do we have standby db?
        has_standby_db = self.has_read_replica_db(CalyxEnv(vm_dim_temp.env))
        # Is it a primary db server or standby db server
        if re.search(r'''STANDBY''', vm_dim_temp.app_role.upper()):
            isPrimaryDb = False
        else:
            isPrimaryDb = True
        # get vm spec from vm sku
        vmSpec: DbAzureVmSpec = DbAzureVmSpec.get_vm_spec_by_sku(self.db, vm_dim_temp.sku)
        # For Azure v2 machine, the number of oracle licensed core is the same as vcpu
        # For other VMs, the number of oracle licensed core is half of the number of vcpu
        if re.search(r'''_V2$''', vm_dim_temp.sku.upper()):
            # v2 VM core is the same as vCPU
            core = vmSpec.cpu
        else:
            core = math.ceil(vmSpec.cpu / 2)

        sku = "oracle_std_proc"

        # for CTMS
        if CalyxApp(vm_dim_temp.app) == CalyxApp.CTMS:
            if has_standby_db:
                if isPrimaryDb:
                    if CalyxEnv(vm_dim_temp.env) is CalyxEnv.NONPRODVAL:
                        sku = "oracle_ent_standby_diag_tuning"
                    else:
                        sku = "oracle_ent_standby"
                else:
                    sku = "oracle_ent_standby"
            else:
                if isPrimaryDb:
                    if CalyxEnv(vm_dim_temp.env) is CalyxEnv.NONPRODVAL:
                        sku = "oracle_ent_proc_diag_tuning"
                    else:
                        if vmSpec.cpu > 8:
                            sku = "oracle_ent_proc"
                        else:
                            sku = "oracle_std_proc"
                else:
                    # does not make sense
                    return

        # for RIM, if has standby db, we must use ENT license, otherwise use standard license
        if CalyxApp(vm_dim_temp.app) == CalyxApp.RIM:
            if has_standby_db:
                sku = "oracle_ent_standby"
            elif isPrimaryDb:
                if vmSpec.cpu > 8:
                    sku = "oracle_ent_proc"
                else:
                    sku = "oracle_std_proc"
            else:
                # does not make sense
                return

        # get the price entry of the license
        db_rsc_price: DbResourcePrice = DbResourcePrice.get_by_sku(self.db, sku)

        # get license quantity per VM
        if sku == "oracle_std_proc":
            qty = vmSpec.cpu / 4
        else:
            qty = core

        db_detail: DbDetailRecord = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv(vm_dim_temp.env),
            app_role=vm_dim_temp.app_role,
            qty=vm_dim_temp.qty * qty,
            lv=BomLevel.SECONDARY,
            bom_type=BomType.LICENSE,
            bom_subtype="Database Licensing"
        )

        return db_detail

    def map_detail_out(self, env: CalyxEnv, din: DbDetailRecord) -> DetailCosts:
        dout: DetailCosts = DetailCosts()
        dout.sku = din.sku
        dout.vendor = din.vendor
        try:
            assert len(din.remark) > 0
            dout.display_name = din.remark
        except:
            dout.display_name = din.sku
        dout.app_role = din.app_role
        dout.qty = din.qty
        dout.currency = din.currency
        dout.unit_price = din.unit_price
        dout.total_price = din.total_price
        dout.bom_type = din.bom_type
        dout.bom_subtype = din.bom_subtype
        dout.billing_type = din.billing_type
        try:
            assert din.vendor == "Azure"
            dout.region = AzureRegion[self.dbSummaryRecords.azure_region].value["primary"]
        except:
            pass
        try:
            assert len(din.resource_type) > 0
            dout.service = din.resource_type
            try:
                assert din.vendor == "Azure" and din.resource_type == "Virtual Machine"
                vm: DimensionTemplate = [x for x in self.templates[env] if x.app_role == din.app_role][0]
                dout.os_type = vm.os_type
                dout.vcpu = self.dbAzureVmSpecDict[din.sku]["cpu"]
                dout.memory = self.dbAzureVmSpecDict[din.sku]["ram"]
                dout.disk_size = self.dbAzureVmSpecDict[din.sku]["storage"]
            except:
                pass
            try:
                assert din.vendor == "Azure" and din.resource_type == "Storage"
                dout.disk_size = self.dbAzureDiskSpecDict[din.sku]
            except:
                pass
        except:
            pass
        return dout

    def get_target_currency(self):
        if self.dbSummaryRecords.azure_region == "CN":
            return Currency.CNY
        else:
            return Currency.USD
