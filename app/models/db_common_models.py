from datetime import datetime
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.mysql import ENUM, INTEGER, VARCHAR, FLOAT, BOOLEAN
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from app.database import Base
from util.common import AzureRegion, BillingType, BomLevel, CalyxApp, CalyxEnv, CalyxRegion, Currency, LinuxDist, \
    OriginAzureRegion, OsType, ServerBackupType, ServerBackupAction, TeeShirtSize


########################################
# Common DB Tables
########################################
class DbProjectRecord(Base):
    """
    Project Headlines
    """
    __tablename__ = 'project_records'
    # __table_args__ = {'extend_existing': True}

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, unique=True, comment='unique uuid of the record')
    app = Column(ENUM(*[x.name for x in CalyxApp]), comment='Calyx application name')
    customer_name = Column(VARCHAR(100), comment='customer name of the estimation, non-essential data')
    project_name = Column(VARCHAR(100), comment='project name of the estimation, non-essential data')
    remark = Column(VARCHAR(255))
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_project_id(cls, db: Session, uuid: str):
        data = db.query(cls).filter_by(uuid=uuid).first()
        return data

    @classmethod
    def update_by_project_id(cls, db: Session, data):
        db.query(cls).filter_by(uuid=data.uuid).update({
            cls.customer_name: data.cutomer_name,
            cls.project_name: data.project_name,
            cls.update_username: data.update_username,
            cls.update_date: datetime.now()
        })

    @classmethod
    def get_by_username(cls, db: Session, username: str):
        data = db.query(cls).filter((cls.create_username == username) | (cls.update_username == username)).all()
        return [x for x in data]

    @classmethod
    def get_by_ownername(cls, db: Session, username: str):
        data = db.query(cls).filter_by(create_username=username).all()
        return [x for x in data]


class DbEnvSummaryRecord(Base):
    """
    Summary Inputs of an environment
    """
    __tablename__ = 'env_summary_records'
    # __table_args__ = {'extend_existing': True}

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, nullable=False, comment='unique uuid of the record')
    version = Column(INTEGER, primary_key=True, default=1, comment='version in project')
    env = Column(ENUM(*[x.name for x in CalyxEnv]), primary_key=True, default='SHARED')
    tshirt_size = Column(ENUM(*[x.name for x in TeeShirtSize]), nullable=False)
    qty = Column(INTEGER, default=1)
    uptime_ratio = Column(FLOAT, default=1, comment='')
    shared_ratio = Column(FLOAT, default=1, comment='')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_project_id_version_env(cls, db: Session, proj_id: str, version: int, env: CalyxEnv):
        data = db.query(cls).filter(
            (cls.uuid == proj_id) & (cls.version == version) & (cls.env == env.value)
        ).first()
        return data


class DbDetailRecord(Base):
    """
    Item level records
    """
    __tablename__ = 'detail_records'
    # __table_args__ = {'extend_existing': True}

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, nullable=False, comment='unique uuid of the record')
    version = Column(INTEGER, primary_key=True, default=1, comment='version in project')
    env = Column(VARCHAR(100), primary_key=True, default=CalyxEnv.SHARED, comment='environment name')
    remark = Column(VARCHAR(255))
    vendor = Column(VARCHAR(100))
    sku = Column(VARCHAR(100))
    qty = Column(INTEGER, default=1)
    app_role = Column(VARCHAR(255), comment='The role of this resource')
    lv = Column(ENUM(*[x.name for x in BomLevel]), default='PRIMARY', comment='main resource or as part of the resource')
    bom_type = Column(VARCHAR(100), nullable=False)
    bom_subtype = Column(VARCHAR(100))
    resource_type = Column(VARCHAR(100))
    billing_type = Column(VARCHAR(100), nullable=False, default=BillingType.ANNUAL)
    unit_price = Column(FLOAT)
    total_price = Column(FLOAT)
    currency = Column(ENUM(*[x.name for x in Currency]), default="CNY")
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_project_id_version_env(cls, db: Session, proj_id: str, version: int, env: CalyxEnv):
        data = db.query(cls).filter((cls.uuid == proj_id) & (cls.version == version) & (cls.env == env.value)).all()
        return [x for x in data]


class DbPriceResult(Base):
    """
    Calculated headline prices
    """
    __tablename__ = 'project_price_results'
    # __table_args__ = {'extend_existing': True}

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, nullable=False, comment='unique uuid of the record')
    version = Column(INTEGER, primary_key=True, default=1, comment='version in project')
    price_name = Column(VARCHAR(100), comment='BOM type and sub type')
    amount = Column(FLOAT)
    currency = Column(ENUM(*[x.name for x in Currency]), default="CNY")
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


########################################
# DB Data Tables
########################################
class DbResourcePrice(Base):
    """
    Resource Prices used in this calculation
    """
    __tablename__ = 'resource_prices'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    vendor = Column(VARCHAR(100), comment='Vendor Name')
    service_name = Column(VARCHAR(100), comment='Azure resources service name, or vendor product categories')
    description = Column(VARCHAR(255), comment='Description of the product')
    sku = Column(VARCHAR(100), nullable=False, comment='sku of the resource, sku+os_type+region to identify the price')
    os_type = Column(ENUM(*[x.name for x in OsType]), comment='operation system of the resource, only for Azure VM')
    currency = Column(ENUM(*[x.name for x in Currency]), nullable=False, default='CNY')
    billing_type = Column(ENUM(*[x.name for x in BillingType]), nullable=False, default='ANNUAL')
    unit_price = Column(FLOAT, nullable=False, comment='annual price or one off cost')
    reservation_term = Column(INTEGER, nullable=False, default=0,
                              comment='contract term of years, only for annual prices')
    azure_region = Column(ENUM(*[x.value for x in OriginAzureRegion]), comment='Only for Azure resources')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_sku(cls, db: Session, sku: str, **kwargs):
        """
        :param db:
        :param sku:
        :param kwargs: other conditions, such as azure region, os, reservation term, and etc
        :return:
        """
        cond = [f"sku = '{sku}'"]
        if "os_type" in kwargs.keys():
            cond.append(f"os_type = '{kwargs['os_type'].value}'")
        sql = f"""
            SELECT * FROM {cls.__tablename__} WHERE {" AND ".join(cond)};
        """
        data = db.execute(sql).first()
        return data

    @classmethod
    def get_by_region_sku(cls, db: Session, sku: str, region: CalyxRegion,
                          contract_term: int = 0, is_primary: bool = True):
        c_region = AzureRegion[region.name]
        if is_primary:
            a_region = c_region.value["primary"]
        else:
            a_region = c_region.value["secondary"]
        data = db.query(cls).filter(
            (cls.sku == sku) &
            (cls.azure_region == a_region) &
            (cls.reservation_term <= contract_term)
        ).order_by(cls.unit_price.asc()).first()
        return data

    @classmethod
    def get_vm_by_region(cls, db: Session, sku: str, region: CalyxRegion, os_type: OsType,
                         contract_term: int, is_primary: bool = True):
        """
        Get vm price by sku + region + os type + contract term + productive/dr region
        :param db: Database Session
        :param sku: SKU of the VM
        :param region: US/EU/CN p.s. this is not Azure Region
        :param os_type: Windows or Linux
        :param contract_term: number of contract years
        :param is_primary: is this VM in production region or DR region
        :return: one db entry, or None
        """
        c_region = AzureRegion[region.name]
        if is_primary:
            a_region = c_region.value["primary"]
        else:
            a_region = c_region.value["secondary"]
        data = db.query(cls).filter(
            (cls.sku == sku) &
            (cls.azure_region == a_region) &
            (cls.os_type == os_type.value) &
            (cls.reservation_term <= contract_term)
        ).order_by(cls.unit_price.asc()).first()
        return data

    @classmethod
    def get_disk_by_region(cls, db: Session, sku: str, region: CalyxRegion,
                           contract_term: int, is_primary: bool = True):
        """
        Get azure disk price by sku + region + contract term + productive/dr region
        :param db: Database Session
        :param sku: SKU of the Disk
        :param region: US/EU/CN p.s. this is not Azure Region
        :param contract_term: number of contract years
        :param is_primary: is this Disk in production region or DR region
        :return: one db entry, or None
        """
        c_region = AzureRegion[region.name]
        if is_primary:
            a_region = c_region.value["primary"]
        else:
            a_region = c_region.value["secondary"]
        data = db.query(cls).filter(
            (cls.sku == sku) &
            (cls.azure_region == a_region) &
            (cls.reservation_term <= contract_term)
        ).order_by(cls.unit_price.asc()).first()
        return data

    @classmethod
    def get_disk_by_size_region(cls, db: Session, disk_size_gb: int, region: CalyxRegion,
                                contract_term: int, is_primary: bool = True, ssd_only: bool = True):
        """
        Get azure disk price by size + region + contract term + productive/dr region
        :param db: Database Session
        :param disk_size_gb: Disk size
        :param region: US/EU/CN p.s. this is not Azure Region
        :param contract_term: number of contract years
        :param is_primary: is this Disk in production region or DR region
        :param ssd_only: only select premium SSD?
        :return: one db entry, or None
        """
        if ssd_only:
            sku = DbAzureDiskSpec.get_ssd_sku_by_disk_size(db, disk_size_gb)
        else:
            sku = DbAzureDiskSpec.get_sku_by_disk_size(db, disk_size_gb)
        if sku is None:
            return
        c_region = AzureRegion[region.name]
        if is_primary:
            a_region = c_region.value["primary"]
        else:
            a_region = c_region.value["secondary"]
        data = db.query(cls).filter(
            (cls.sku == sku) &
            (cls.azure_region == a_region) &
            (cls.reservation_term <= contract_term)
        ).order_by(cls.unit_price.asc()).first()
        return data


class DbBackupRatio(Base):
    """
    Resource Prices used in this calculation
    """
    __tablename__ = 'backup_ratio'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    env = Column(ENUM(*[x.name for x in CalyxEnv]), primary_key=True, comment='environment name')
    server_type = Column(ENUM(*[x.name for x in ServerBackupType]), nullable=False, comment='server usage type')
    action = Column(ENUM(*[x.name for x in ServerBackupAction]), nullable=False, comment='backup action types')
    ratio = Column(FLOAT, nullable=False, comment='compress ratio')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_backup_ratio(cls, db: Session,
                         env: CalyxEnv,
                         server_type: ServerBackupType,
                         server_action: ServerBackupAction
                         ) -> float:
        data = db.query(cls).filter((cls.env == env.value) &
                                    (cls.server_type == server_type.value) &
                                    (cls.server_action == server_action.value)).first()
        try:
            return data.ratio
        except:
            return 0

    @classmethod
    def get_backup_ratio_dict(cls, db: Session
                              ) -> Dict[CalyxEnv, Dict[ServerBackupType, Dict[ServerBackupAction, float]]]:
        ret = {}
        data = cls.get_all(db)
        for d in data:
            env = CalyxEnv(d.env)
            serverType = ServerBackupType(d.server_type)
            action = ServerBackupAction(d.action)
            try:
                ret[env]
            except:
                ret[env] = {}
            try:
                ret[env][serverType]
            except:
                ret[env][serverType] = {}
            ret[env][serverType][action] = d.ratio
        return ret


class DimensionTemplate(Base):
    """
    Dimension templates, or T-Shirt size of the Application
    """
    __tablename__ = 'dimension_templates'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    app = Column(ENUM(*[x.name for x in CalyxApp]), comment='Calyx application name')
    env = Column(ENUM(*[x.name for x in CalyxEnv]), comment='environment name')
    tshirt_size = Column(ENUM(*[x.name for x in TeeShirtSize]), nullable=False)
    app_role = Column(VARCHAR(255), nullable=False, comment='The role of this resource')
    sku = Column(VARCHAR(100), nullable=False, comment='sku of the resource, sku+os_type+region to identify the price')
    os_type = Column(ENUM(*[x.name for x in OsType]), comment='operation system of the resource, only for Azure VM')
    qty = Column(INTEGER, nullable=False, comment='quantity of the resource')
    is_asr_required = Column(BOOLEAN, nullable=False, default=True, comment='only prod and db need ASR')
    backup_type = Column(ENUM(*[x.name for x in ServerBackupType]), comment='backup plan name')
    weekly_data_chg_rate = Column(FLOAT, nullable=False, default=0)
    disk1 = Column(VARCHAR(100), comment='OS Disk sku name, usually P10:128G')
    disk2 = Column(VARCHAR(100), comment='App Disk sku name, usually P6:64G or P10:128G')
    linux_dist = Column(ENUM(*[x.name for x in LinuxDist]), comment='linux distribution for linux OS')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_env_types(cls, db: Session, app: CalyxApp, tshirt_size: TeeShirtSize) -> List:
        sql = f'''
            SELECT DISTINCT env 
            FROM {cls.__tablename__}
            WHERE app='{app.value}'
            AND tshirt_size='{tshirt_size.value}'
        '''
        res = db.execute(sql).all()
        return [x.env for x in res]

    @classmethod
    def get_main_sku(cls, db: Session, app: CalyxApp, tshirt_size: TeeShirtSize) -> Dict:
        env_types = cls.get_env_types(db, app, tshirt_size)
        ret = {}
        for _env in env_types:
            env = CalyxEnv(_env)
            ret[env] = [x for x in db.query(cls).filter(
                (cls.app == app.value) &
                (cls.tshirt_size == tshirt_size.value) &
                (cls.env == env)
            ).all()]
        return ret


class DbAzureVmSpec(Base):
    """
    Azure VM Specification
    """
    __tablename__ = 'azure_vm_spec'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    sku = Column(VARCHAR(100), nullable=False)
    cpu = Column(INTEGER, nullable=False)
    ram = Column(FLOAT, nullable=False, comment='Unit: GB')
    storage = Column(INTEGER, comment='Unit: GB')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_vm_spec_by_sku(cls, db: Session, sku: str):
        data = db.query(cls).filter(cls.sku == sku).first()
        return data

    @classmethod
    def get_vm_spec_dict(cls, db: Session) -> Dict[str, Dict]:
        ret = {}
        data = cls.get_all(db)
        for d in data:
            ret[d.sku] = {"cpu": d.cpu, "ram": d.ram, "storage": d.storage}
        return ret


class DbAzureDiskSpec(Base):
    """
    Azure Disk Specification
    """
    __tablename__ = 'azure_disk_spec'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    sku = Column(VARCHAR(100), nullable=False)
    storage = Column(INTEGER, nullable=False, comment='Unit: GB')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_ssd_sku_by_disk_size(cls, db: Session, disk_size_gb: int) -> Optional[str]:
        data = db.query(cls).filter(
            (cls.storage >= disk_size_gb) &
            (cls.sku.like('P%'))
        ).order_by(cls.storage.asc()).first()
        try:
            assert len(data.sku) > 0
            return data.sku
        except:
            return None

    @classmethod
    def get_sku_by_disk_size(cls, db: Session, disk_size_gb: int) -> Optional[str]:
        data = db.query(cls).filter(cls.storage >= disk_size_gb).order_by(cls.storage.asc()).first()
        try:
            assert len(data.sku) > 0
            return data.sku
        except:
            return None

    @classmethod
    def get_disk_size_by_sku(cls, db: Session, sku: str) -> Optional[int]:
        data = db.query(cls).filter(cls.sku == sku).first()
        return data.storage

    @classmethod
    def get_disk_spec_dict(cls, db: Session) -> Dict[str, int]:
        ret = {}
        data = cls.get_all(db)
        for d in data:
            ret[d.sku] = d.storage
        return ret


class DbExchangeRate(Base):
    """
    currency exchange rate
    """
    __tablename__ = 'exchange_rate'
    # __table_args__ = {'extend_existing': True}
    id = Column(INTEGER, primary_key=True)
    currency = Column(ENUM(*[x.name for x in Currency]), nullable=False, comment='Currency code')
    rate = Column(FLOAT, nullable=False, default=1, comment='exchange rate to USD')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_exchange_rate_dict(cls, db: Session) -> Dict[Currency, float]:
        ret = {}
        data = cls.get_all(db)
        for d in data:
            ret[Currency(d.currency)] = d.rate
        return ret


########################################
# RIM specific DB tables and views
########################################
class DbRimSummaryRecords(Base):
    """
    Table rim_summary_records
    """
    __tablename__ = 'rim_summary_records'

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, nullable=False, comment='unique uuid of the record')
    version = Column(INTEGER, primary_key=True, default=1, comment='version in project')
    remark = Column(VARCHAR(255), default='', comment='remark of this version')
    is_customized = Column(BOOLEAN, default=False, comment='is this estimation based on t-shirt templates')
    discount = Column(FLOAT, default=0, comment='overall discount')
    total_reg_users = Column(INTEGER, default=0)
    conc_reg_users = Column(INTEGER, default=0)
    total_pub_users = Column(INTEGER, default=0)
    conc_pub_users = Column(INTEGER, default=0)
    total_view_users = Column(INTEGER, default=0)
    conc_view_users = Column(INTEGER, default=0)
    prod_envs = Column(INTEGER, default=1, comment='Number of productive environments')
    nonprodval_envs = Column(INTEGER, default=0, comment='Number of non-productive validation environments')
    nonprod_envs = Column(INTEGER, default=0, comment='Number of non-productive environments(Sandbox)')
    is_multitenant = Column(BOOLEAN, default=True)
    multitenant_db_ratio = Column(FLOAT, default=0.0625, comment='A tenant uses 6.25% of the DB')
    has_prod_read_replica_db = Column(BOOLEAN, default=True)
    has_nonprodval_read_replica_db = Column(BOOLEAN, default=True)
    has_nonprod_read_replica_db = Column(BOOLEAN, default=True)
    has_citrix = Column(BOOLEAN, default=True)
    db_storage_gb = Column(INTEGER, default=512)
    azure_region = Column(ENUM(*[x.name for x in CalyxRegion]), default='CN')
    currency = Column(ENUM(*[x.name for x in Currency]), default='CNY')
    contract_term = Column(INTEGER, default=3)
    has_power_bi = Column(BOOLEAN, default=False)
    report_creators = Column(INTEGER, default=0)
    super_users = Column(INTEGER, default=0)
    standard_users = Column(INTEGER, default=0)
    azure_fileshare_storage_gb = Column(INTEGER, default=0, comment='if we provide file share')
    azure_fileshare_sync_servers = Column(INTEGER, default=1, comment='if we provide file share')
    has_azure_ri_discount = Column(BOOLEAN, default=True, comment='user 1-year or 3-year RI rate if possible')
    has_vendor_discount = Column(BOOLEAN, default=True, comment='Vendor pre-agreed discounts included (e.g. Oracle)')
    sla = Column(FLOAT, default=0.995, comment='99.5% Availability')
    has_dr = Column(BOOLEAN, default=True, comment='has Disaster Recovery design')
    dr_rpo = Column(INTEGER, default=1, comment='1 hour RPO')
    dr_rto = Column(INTEGER, default=8, comment='8 hour RPO')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_project_id_version(cls, db: Session, project_id: str, version: int):
        data = db.query(cls).filter((cls.uuid == project_id) & (cls.version == version)).first()
        return data


class DbRimTeeShirtSize(Base):
    """Table rim_tshirt_size"""
    __tablename__ = 'rim_tshirt_size'

    id = Column(INTEGER, primary_key=True)
    tshirt_size = Column(ENUM(*[x.name for x in TeeShirtSize]))
    db_size_upper = Column(INTEGER)
    azure_file_usage = Column(FLOAT)
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_all(cls, db: Session) -> List:
        """
        The sorted T-Shirt size of RIM system
        """
        data = db.query(cls).order_by(cls.db_size_upper.asc()).all()
        return [x for x in data]

    @classmethod
    def get_by_size(cls, db: Session, size: TeeShirtSize):
        data = db.query(cls).filter_by(tshirt_size=size.value).first()
        return data


########################################
# CTMS specific DB tables and views
########################################
class DbCtmsSummaryRecords(Base):
    """
    Table ctms_summary_records
    """
    __tablename__ = 'ctms_summary_records'

    id = Column(INTEGER, primary_key=True)
    uuid = Column(VARCHAR(100), primary_key=True, nullable=False, comment='unique uuid of the record')
    version = Column(INTEGER, primary_key=True, default=1, comment='version in project')
    remark = Column(VARCHAR(255), default='', comment='remark of this version')
    is_customized = Column(BOOLEAN, default=False, comment='is this estimation based on t-shirt templates')
    discount = Column(FLOAT, default=0, comment='overall discount')
    total_reg_users = Column(INTEGER, default=0)
    conc_reg_users = Column(INTEGER, default=0)
    total_pub_users = Column(INTEGER, default=0)
    conc_pub_users = Column(INTEGER, default=0)
    total_view_users = Column(INTEGER, default=0)
    conc_view_users = Column(INTEGER, default=0)
    is_multitenant = Column(BOOLEAN, default=True)
    multitenant_db_ratio = Column(FLOAT, default=0.0625, comment='A tenant uses 6.25% of the DB')
    has_prod_read_replica_db = Column(BOOLEAN, default=True)
    has_nonprodval_read_replica_db = Column(BOOLEAN, default=True)
    has_nonprod_read_replica_db = Column(BOOLEAN, default=True)
    has_citrix = Column(BOOLEAN, default=True)
    db_storage_gb = Column(INTEGER, default=512)
    azure_region = Column(ENUM(*[x.name for x in CalyxRegion]), default='CN')
    currency = Column(ENUM(*[x.name for x in Currency]), default='CNY')
    contract_term = Column(INTEGER, default=3)
    has_power_bi = Column(BOOLEAN, default=False)
    report_creators = Column(INTEGER, default=0)
    super_users = Column(INTEGER, default=0)
    standard_users = Column(INTEGER, default=0)
    azure_fileshare_storage_gb = Column(INTEGER, default=0, comment='if we provide file share')
    azure_fileshare_sync_servers = Column(INTEGER, default=1, comment='if we provide file share')
    has_azure_ri_discount = Column(BOOLEAN, default=True, comment='user 1-year or 3-year RI rate if possible')
    has_vendor_discount = Column(BOOLEAN, default=True, comment='Vendor pre-agreed discounts included (e.g. Oracle)')
    sla = Column(FLOAT, default=0.995, comment='99.5% Availability')
    has_dr = Column(BOOLEAN, default=True, comment='has Disaster Recovery design')
    dr_rpo = Column(INTEGER, default=1, comment='1 hour RPO')
    dr_rto = Column(INTEGER, default=8, comment='8 hour RPO')
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class DbCtmsTeeShirtSize(Base):
    """Table ctms_tshirt_size"""
    __tablename__ = 'ctms_tshirt_size'

    id = Column(INTEGER, primary_key=True)
    tshirt_size = Column(ENUM(*[x.name for x in TeeShirtSize]))
    db_size_upper = Column(INTEGER)
    azure_file_usage = Column(FLOAT)
    create_username = Column(VARCHAR(100), comment="user who first created it")
    update_username = Column(VARCHAR(100), comment="user who latest updated it")
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_all(cls, db: Session) -> List:
        """
        The sorted T-Shirt size of CTMS system
        """
        data = db.query(cls).order_by(cls.db_size_upper.asc()).all()
        return [x for x in data]
