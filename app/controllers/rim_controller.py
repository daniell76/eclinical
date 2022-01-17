import math

from copy import deepcopy
from typing import List

from app.controllers.common_controllers import AppCalculator
from app.models.db_common_models import DbProjectRecord, DbEnvSummaryRecord, DbRimSummaryRecords, DbDetailRecord, \
    DbPriceResult, DbResourcePrice, DbRimTeeShirtSize, DimensionTemplate, DbAzureDiskSpec

from app.models.data_rim_models import RimCostOut, RimSpecIn, RimOutMisc

from util.common import *


class RimCalculator(AppCalculator):

    def __init__(self, *args, **kwargs):
        super(RimCalculator, self).__init__(*args, **kwargs)
        self.lst_tshirt_sizes = DbRimTeeShirtSize.get_all(self.db)
        self.tshirt_size = TeeShirtSize.XSMALL

    def gen_api_summary_out(self, detail: bool = True):
        """
        Convert calculation results to API output format
        API output results are stored in self.summaryResultOut
        Must be called after the BOM list been generated,
        i.e. self.dbProjRecord, self.dbEnvRecords, self.dbDetailRecords, and dbSummaryRecords are ready
        :param detail: whether include detail BOM or not
        :return:
        """
        self.summaryResultOut = RimCostOut()

        self.summaryResultOut.projInfo.projId = self.projId
        self.summaryResultOut.projInfo.customerName = self.dbProjRecord.customer_name
        self.summaryResultOut.projInfo.projName = self.dbProjRecord.project_name
        self.summaryResultOut.projInfo.remark = self.dbSummaryRecords.remark
        self.summaryResultOut.projInfo.version = self.version
        self.summaryResultOut.projInfo.createdBy = self.user

        self.summaryResultOut.yearlySummaryCost.labor = self.calc_sum_by_bom_type(BomType.LABOR)
        self.summaryResultOut.yearlySummaryCost.infra = self.calc_sum_by_bom_type(BomType.INFRA)
        self.summaryResultOut.yearlySummaryCost.licenses = self.calc_sum_by_bom_type(BomType.LICENSE)
        self.summaryResultOut.yearlySummaryCost.total = \
            self.summaryResultOut.yearlySummaryCost.labor + \
            self.summaryResultOut.yearlySummaryCost.infra + \
            self.summaryResultOut.yearlySummaryCost.licenses

        try:
            assert self.tshirt_size
            if self.summaryResultOut.misc is None:
                self.summaryResultOut.misc = RimOutMisc()
                self.summaryResultOut.misc.tshirt_size = self.tshirt_size
        except:
            pass

        self.summaryResultOut.yearlyDetailCost.azureServers = self.calc_sum_by_bom_subtype("Azure Servers")
        self.summaryResultOut.yearlyDetailCost.azureSharedServices = \
            self.calc_sum_by_bom_subtype("Azure Shared Services")
        self.summaryResultOut.yearlyDetailCost.serverSoftwareLicensing = \
            self.calc_sum_by_bom_subtype("Server Software Licensing")
        self.summaryResultOut.yearlyDetailCost.backupServices = \
            self.calc_sum_by_bom_subtype("Backup Service")
        self.summaryResultOut.yearlyDetailCost.databaseLicensing = \
            self.calc_sum_by_bom_subtype("Database Licensing")
        self.summaryResultOut.yearlyDetailCost.azureNetworkServices = \
            self.calc_sum_by_bom_subtype("Azure Network Service")
        self.summaryResultOut.yearlyDetailCost.clientSoftwareLicensing = \
            self.calc_sum_by_bom_subtype("Client Software Licensing")
        self.summaryResultOut.yearlyDetailCost.azurePowerBi = self.calc_sum_by_bom_subtype("Power BI")
        self.summaryResultOut.yearlyDetailCost.azureFileShare = self.calc_sum_by_bom_subtype("Azure File Share")
        self.summaryResultOut.yearlyDetailCost.managedServices = self.calc_sum_by_bom_subtype("Managed Services")
        self.summaryResultOut.yearlyDetailCost.total = \
            self.summaryResultOut.yearlyDetailCost.azureServers + \
            self.summaryResultOut.yearlyDetailCost.azureSharedServices + \
            self.summaryResultOut.yearlyDetailCost.serverSoftwareLicensing + \
            self.summaryResultOut.yearlyDetailCost.backupServices + \
            self.summaryResultOut.yearlyDetailCost.databaseLicensing + \
            self.summaryResultOut.yearlyDetailCost.azureNetworkServices + \
            self.summaryResultOut.yearlyDetailCost.clientSoftwareLicensing + \
            self.summaryResultOut.yearlyDetailCost.azurePowerBi + \
            self.summaryResultOut.yearlyDetailCost.azureFileShare + \
            self.summaryResultOut.yearlyDetailCost.managedServices

        if detail:
            self.gen_api_detail_out()
            self.summaryResultOut.details = self.detailResultOut

    def gen_api_detail_out(self):
        self.detailResultOut = []
        so = {'SHARED': 1, 'PROD': 2, 'NONPRODVAL': 3, 'NONPROD': 4}
        for env in sorted(self.dbDetailRecords.keys(), key=lambda x: so[x.name]):
            for din in [x for x in self.dbDetailRecords[env] if x.lv == BomLevel.PRIMARY]:
                dout = self.map_detail_out(env, din)
                sum_total_price = 0
                for din2 in [x for x in self.dbDetailRecords[env] if x.app_role == din.app_role and x.lv == BomLevel.SECONDARY]:
                    try:
                        assert len(dout.components) > 0
                    except:
                        dout.components = []
                    dout2 = self.map_detail_out(env, din2)
                    dout.components.append(dout2)
                    sum_total_price += dout2.total_price
                if sum_total_price > 0:
                    dout.sum_total_price = dout.total_price + sum_total_price
                self.detailResultOut.append(dout)

    def load_api_summary_out(self, detail: bool = True):
        """
        Load project price calculation results from DB
        self.projId and self.version must be a valid value
        if detail results required, self.dbDetailRecords must be loaded with valid values
        detail results are not formatted in DB, and will always be generated based on self.dbDetailRecords
        :param detail: whether to load BOM details or not
        :return:
        """
        lstDbPrices: List[DbPriceResult] = DbPriceResult.get_by_project_version(self.db, self.projId, self.version)
        dbPrices = dict((x.price_name, x.amount) for x in lstDbPrices)
        self.summaryResultOut = RimCostOut()

        self.summaryResultOut.projInfo.projId = self.projId
        self.summaryResultOut.projInfo.customerName = self.dbProjRecord.customer_name
        self.summaryResultOut.projInfo.projName = self.dbProjRecord.project_name
        self.summaryResultOut.projInfo.remark = self.dbSummaryRecords.remark
        self.summaryResultOut.projInfo.version = self.dbSummaryRecords.version
        self.summaryResultOut.projInfo.createdBy = self.user

        self.summaryResultOut.yearlySummaryCost.labor = dbPrices["labor"]
        self.summaryResultOut.yearlySummaryCost.infra = dbPrices["infra"]
        self.summaryResultOut.yearlySummaryCost.licenses = dbPrices["licenses"]
        self.summaryResultOut.yearlySummaryCost.total = dbPrices["total"]

        self.summaryResultOut.yearlyDetailCost.azureServers = dbPrices["azureServers"]
        self.summaryResultOut.yearlyDetailCost.azureSharedServices = dbPrices["azureSharedServices"]
        self.summaryResultOut.yearlyDetailCost.serverSoftwareLicensing = dbPrices["serverSoftwareLicensing"]
        self.summaryResultOut.yearlyDetailCost.backupServices = dbPrices["backupServices"]
        self.summaryResultOut.yearlyDetailCost.databaseLicensing = dbPrices["databaseLicensing"]
        self.summaryResultOut.yearlyDetailCost.azureNetworkServices = dbPrices["azureNetworkServices"]
        self.summaryResultOut.yearlyDetailCost.clientSoftwareLicensing = dbPrices["clientSoftwareLicensing"]
        self.summaryResultOut.yearlyDetailCost.azurePowerBi = dbPrices["azurePowerBi"]
        self.summaryResultOut.yearlyDetailCost.azureFileShare = dbPrices["azureFileShare"]
        self.summaryResultOut.yearlyDetailCost.managedServices = dbPrices["managedServices"]
        self.summaryResultOut.yearlyDetailCost.total = dbPrices["total"]

        if detail:
            self.gen_api_detail_out()
            self.summaryResultOut.details = self.detailResultOut

    def calc_sum_by_bom_type(self, bom_type: BomType):
        ret = 0
        try:
            for env in self.dbDetailRecords:
                ret += sum([x.total_price for x in self.dbDetailRecords[env] if x.bom_type == bom_type])
        except:
            pass
        return ret

    def calc_sum_by_bom_subtype(self, bom_subtype: str):
        ret = 0
        try:
            for env in self.dbDetailRecords:
                ret += sum([x.total_price for x in self.dbDetailRecords[env] if x.bom_subtype == bom_subtype])
        except:
            pass
        return ret

    def new_proj(self):
        """
        create a new project based on input SpecIn object
        :return
        """

        # create a new DB entry for this project, mainly for project id and version
        self.dbProjRecord = self.new_db_proj_record()
        self.dbProjRecord.app = CalyxApp.RIM.value
        self.projId = self.dbProjRecord.uuid
        # no need to verify if the project id is used, it is already verified when creating
        # assert DbEnvSummaryRecord.get_max_version(self.db, self.projId) == 0
        self.version = 1

        # Record the input parameters
        self.dbSummaryRecords = self.new_db_proj_summary()

        # get the dimension of this version
        self.get_tshirt_size()

        # create new version contents
        self.new_proj_version(self.version)

    def create_db_proj(self):
        DbProjectRecord.add(self.db, self.dbProjRecord)
        self.db.commit()

    def create_db_proj_version(self):
        """
        Save contents to DB tables:
        env_summary_records, detail_records, rim_summary_records, project_price_results
        must be called after all the calculation is done
        :return:
        """
        for db_env in self.dbEnvRecords.values():
            DbEnvSummaryRecord.add(self.db, db_env)
        for db_detail_list in self.dbDetailRecords.values():
            for db_detail in db_detail_list:
                DbDetailRecord.add(self.db, db_detail)
        DbRimSummaryRecords.add(self.db, self.dbSummaryRecords)

        self.create_db_proj_version_results()

        self.db.commit()

    def create_db_proj_version_results(self):
        """
        Save the summary price results of a project version.
        Must be called after all the calculation is done
        :return:
        """
        # create a Price model
        priceTemplate = DbPriceResult(
            uuid=self.projId,
            version=self.version,
            currency=self.get_target_currency().value,
            create_username=self.user if self.original_author is None else self.original_author,
            update_username=self.user,
            create_date=self.original_create_time
        )
        for k in self.summaryResultOut.yearlySummaryCost.dict():
            p = deepcopy(priceTemplate)
            p.price_name = k
            p.amount = self.summaryResultOut.yearlySummaryCost.dict()[k]
            DbPriceResult.add(self.db, p)
        for k in self.summaryResultOut.yearlyDetailCost.dict():
            if k == "total":
                continue
            p = deepcopy(priceTemplate)
            p.price_name = k
            p.amount = self.summaryResultOut.yearlyDetailCost.dict()[k]
            DbPriceResult.add(self.db, p)

    def update_db_proj_version_result(self):
        """
        Update only the price result to DB tables:
        project_price_results
        delete all the old records identified by project_id + version, and then save the new version
        typically called after the customize project calculation
        must be called after all the calculation is done
        :return:
        """
        DbPriceResult.delete_by_project_version(db=self.db, uuid=self.projId, version=self.version)
        self.create_db_proj_version_results()
        self.db.commit()

    def new_proj_version(self, version: int = None):
        """
        must be called after self.dbProjRecord, self.dbSummaryRecords, self.projId are set
        :return:
        """
        try:
            assert version > 0
            self.version = version
        except:
            # get the max version number
            current_version = DbEnvSummaryRecord.get_max_version(self.db, self.projId)
            # add 1 to the new version
            self.version = current_version + 1
        # create new version contents
        self.new_version_content()

    def new_version_content(self):
        """
        create the content of a new project version
        self.dbProjRecord, self.dbSummaryRecords, self.projId, self.version before call this method.
        """

        # create new db environment entries
        self.new_db_env_records()

        # create all BOM entries for each environment
        self.new_db_detail_records()

    def new_db_proj_summary(self):
        """
        Must be called after the project ID is created.
        self.specIn must have correct value
        Number of productive environments must be greater than 0
        This is the mapping method from input API parameters (SpecIn) to DB records (rim_summary_records)
        """
        assert self.projId, "No project ID!"
        assert self.specIn.environments.nProdEnv > 0, "No productive environments"
        param = {
            "uuid": self.projId,
            "version": self.version,
            "remark": "",
            "is_customized": False,
            "discount": self.specIn.project.discount,
            "total_reg_users": self.specIn.users.totalRegistrationUsers,
            "conc_reg_users": self.specIn.users.concurrentRegistrationUsers,
            "total_pub_users": self.specIn.users.totalPublishUsers,
            "conc_pub_users": self.specIn.users.concurrentPublishUsers,
            "total_view_users": self.specIn.users.totalViewUsers,
            "conc_view_users": self.specIn.users.concurrentViewUsers,
            "prod_envs": self.specIn.environments.nProdEnv,
            "nonprodval_envs": self.specIn.environments.nNonProdValidatedEnv,
            "nonprod_envs": self.specIn.environments.nNonProdEnv,
            "is_multitenant": self.specIn.misc.isMultiTenant,
            "multitenant_db_ratio": self.specIn.misc.multiTenantDbRatio,
            "has_prod_read_replica_db": self.specIn.misc.hasProdReadReplicaDatabase,
            "has_nonprodval_read_replica_db": self.specIn.misc.hasNonProdValReadReplicaDatabase,
            "has_nonprod_read_replica_db": self.specIn.misc.hasNonProdReadReplicaDatabase,
            "has_citrix": self.specIn.misc.hasCitrix,
            "db_storage_gb": self.specIn.misc.dbStorage,
            "azure_region": self.specIn.misc.azureRegion,
            "currency": Currency.CNY if self.specIn.misc.azureRegion is CalyxRegion.CN else Currency.USD,
            "contract_term": self.specIn.misc.contractTerm,
            "has_power_bi": self.specIn.analytics.hasPowerBi,
            "report_creators": self.specIn.analytics.reportCreators,
            "super_users": self.specIn.analytics.superUsers,
            "standard_users": self.specIn.analytics.standardUser,
            "azure_fileshare_storage_gb": self.specIn.azureFileShare.azureFileShareStorage,
            "azure_fileshare_sync_servers": self.specIn.azureFileShare.azureFilesShareSyncServers,
            "has_azure_ri_discount": self.specIn.internal.useAzureRiRate,
            "has_vendor_discount": self.specIn.internal.hasVendorDiscount,
            "sla": self.specIn.internal.slaTarget,
            "has_dr": self.specIn.internal.hasDisasterRecovery,
            "dr_rpo": self.specIn.internal.drRpo,
            "dr_rto": self.specIn.internal.drRto,
            "create_username": self.user if self.original_author is None else self.original_author,
            "update_username": self.user,
            "create_date": self.original_create_time
        }
        db_sum = DbRimSummaryRecords(**param)
        return db_sum

    def load_db_proj_summary(self):
        """
        read the Spec of a give project version
        self.projId and self.version must be a valid value
        :return:
        """
        self.dbSummaryRecords = DbRimSummaryRecords.get_by_project_id_version(self.db, self.projId, self.version)
        if self.dbSummaryRecords is not None:
            self.specIn = self.db_rim_summary_records_to_spec_in(self.dbSummaryRecords)
            if self.dbProjRecord is not None:
                self.specIn.project.customer_name = self.dbProjRecord.customer_name
                self.specIn.project.project_name = self.dbProjRecord.project_name

    def new_db_detail_records(self):
        """
        must be called after the project and env db object has been created/loaded
        Create all the detailed BoM of each elements based templates

        :return:
        """
        # load RIM templates according to the T-Shirt size
        self.templates = DimensionTemplate.get_main_sku(self.db, CalyxApp.RIM, self.tshirt_size)
        ######################################################################
        # loop through all the environments to create BoM lists
        ######################################################################
        for env in self.dbEnvRecords:
            self.dbDetailRecords[env] = []
            try:
                assert len(self.templates[env]) > 0
            except:
                continue
            ######################################################################
            # Process all the VM templates
            ######################################################################
            for db_dim_temp in self.templates[env]:
                ######################################################################
                # Create the auxiliary entries for the VM, depends on the app role
                ######################################################################
                # initialize secondary BoM list of the VM
                lstAuxRsc = []
                # loop through each app role
                if db_dim_temp.app_role == "Citrix":
                    if not self.dbSummaryRecords.has_citrix:
                        continue
                    # MS Office License
                    sku = "ms_office_cost"
                    db_rsc_price: DbResourcePrice = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LICENSE,
                        bom_subtype="Client Software Licensing"
                    )
                    lstAuxRsc.append(db_detail)
                elif db_dim_temp.app_role == "File Server":
                    if self.dbSummaryRecords.azure_fileshare_storage_gb <= 0:
                        continue
                    # add file share storages. This VM is always in a shared environment
                    db_rsc_price: DbResourcePrice = DbResourcePrice.get_disk_by_size_region(
                        db=self.db,
                        disk_size_gb=self.dbSummaryRecords.azure_fileshare_storage_gb,
                        region=CalyxRegion(self.dbSummaryRecords.azure_region),
                        contract_term=self.dbSummaryRecords.contract_term
                    )
                    if db_rsc_price is None:
                        # default is to P20: 512GB
                        db_rsc_price = DbResourcePrice.get_disk_by_region(
                            db=self.db,
                            sku="P20",
                            region=CalyxRegion(self.dbSummaryRecords.azure_region),
                            contract_term=self.dbSummaryRecords.contract_term
                        )
                    db_detail = self.new_db_bom_disk_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty
                    )
                    lstAuxRsc.append(db_detail)
                elif db_dim_temp.app_role == "InSight Manager":
                    pass
                elif db_dim_temp.app_role == "Rendering":
                    # MS Office License
                    sku = "ms_office_cost"
                    db_rsc_price: DbResourcePrice = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LICENSE,
                        bom_subtype="Client Software Licensing"
                    )
                    lstAuxRsc.append(db_detail)
                elif db_dim_temp.app_role == "Viewing":
                    pass
                elif db_dim_temp.app_role == "Micro Services":
                    pass
                elif db_dim_temp.app_role == "Database":
                    # Database license fee for primary db
                    db_detail = self.get_vm_oracle_lic(db_dim_temp)
                    lstAuxRsc.append(db_detail)
                    # Database Setup Fee
                    sku = "db_setup"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LABOR,
                        bom_subtype="Managed Services"
                    )
                    lstAuxRsc.append(db_detail)
                    # Database quiessence/maintenance events - 4 for each database
                    sku = "db_case"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LABOR,
                        bom_subtype="Managed Services"
                    )
                    lstAuxRsc.append(db_detail)
                elif db_dim_temp.app_role == "Standby Database":
                    if not self.has_read_replica_db(env):
                        continue
                    # Database license fee for primary db
                    db_detail = self.get_vm_oracle_lic(db_dim_temp)
                    lstAuxRsc.append(db_detail)
                    # Database Setup Fee
                    sku = "db_setup"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LABOR,
                        bom_subtype="Managed Services"
                    )
                    lstAuxRsc.append(db_detail)
                    # Database quiessence/maintenance events - 4 for each database
                    sku = "db_case"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.LABOR,
                        bom_subtype="Managed Services"
                    )
                    lstAuxRsc.append(db_detail)
                else:
                    continue
                ################################################################################
                # Create the primary entry for the VM
                ################################################################################
                # Get the price object of the VM
                db_vm_price: DbResourcePrice = DbResourcePrice.get_vm_by_region(
                    db=self.db,
                    sku=db_dim_temp.sku,
                    region=CalyxRegion(self.dbSummaryRecords.azure_region),
                    os_type=OsType(db_dim_temp.os_type),
                    contract_term=self.dbSummaryRecords.contract_term
                )
                # Create BoM entry of the VM
                db_vm_detail = self.new_db_bom_vm_from_price(db_vm_price, env, db_dim_temp.app_role, db_dim_temp.qty)
                self.dbDetailRecords[env].append(db_vm_detail)
                ################################################################################
                # Create disk entries for the VM
                ################################################################################
                vm_disk_size = 0
                # all VMs have 1 x os disk
                sku = db_dim_temp.disk1
                try:
                    assert len(sku) > 0
                    db_rsc_price: DbResourcePrice = DbResourcePrice.get_disk_by_region(
                        db=self.db,
                        sku=sku,
                        region=CalyxRegion(self.dbSummaryRecords.azure_region),
                        contract_term=self.dbSummaryRecords.contract_term
                    )
                    db_detail = self.new_db_bom_disk_from_price(
                        db_rsc_price, env, db_dim_temp.app_role, db_dim_temp.qty)
                    self.dbDetailRecords[env].append(db_detail)
                    if db_dim_temp.is_asr_required:
                        db_detail_cp = deepcopy(db_detail)
                        if db_detail_cp.remark is None:
                            db_detail_cp.remark = 'ASR'
                        else:
                            db_detail_cp.remark = ' - '.join([db_detail_cp.remark, 'ASR'])
                        self.dbDetailRecords[env].append(db_detail)
                    vm_disk_size += DbAzureDiskSpec.get_disk_size_by_sku(self.db, sku) * db_dim_temp.qty
                except:
                    pass
                # most of the VMs, except "Citrix", has local storage disks defined in `disk2`
                sku = db_dim_temp.disk2
                if db_dim_temp.app_role != "Citrix":
                    try:
                        assert len(sku) > 0
                        db_rsc_price: DbResourcePrice = DbResourcePrice.get_disk_by_region(
                            db=self.db,
                            sku=sku,
                            region=CalyxRegion(self.dbSummaryRecords.azure_region),
                            contract_term=self.dbSummaryRecords.contract_term
                        )
                        db_detail = self.new_db_bom_disk_from_price(db_rsc_price, env, db_dim_temp.app_role,
                                                                    db_dim_temp.qty)
                        self.dbDetailRecords[env].append(db_detail)
                        if db_dim_temp.is_asr_required:
                            db_detail_cp = deepcopy(db_detail)
                            if db_detail_cp.remark is None:
                                db_detail_cp.remark = 'ASR'
                            else:
                                db_detail_cp.remark = ' - '.join([db_detail_cp.remark, 'ASR'])
                            self.dbDetailRecords[env].append(db_detail)
                        vm_disk_size += DbAzureDiskSpec.get_disk_size_by_sku(self.db, sku) * db_dim_temp.qty
                    except:
                        pass
                # DB servers got 4 extra storage disks, defined in `db_storage_gb`
                if db_dim_temp.app_role == "Database" or db_dim_temp.app_role == "Standby Database":
                    db_rsc_price: DbResourcePrice = DbResourcePrice.get_disk_by_size_region(
                        db=self.db,
                        disk_size_gb=self.dbSummaryRecords.db_storage_gb,
                        region=CalyxRegion(self.dbSummaryRecords.azure_region),
                        contract_term=self.dbSummaryRecords.contract_term
                    )
                    db_detail = self.new_db_bom_disk_from_price(db_rsc_price, env, db_dim_temp.app_role,
                                                                db_dim_temp.qty * 4)
                    self.dbDetailRecords[env].append(db_detail)
                    if db_dim_temp.is_asr_required:
                        db_detail_cp = deepcopy(db_detail)
                        if db_detail_cp.remark is None:
                            db_detail_cp.remark = 'ASR'
                        else:
                            db_detail_cp.remark = ' - '.join([db_detail_cp.remark, 'ASR'])
                        self.dbDetailRecords[env].append(db_detail)
                    vm_disk_size += DbAzureDiskSpec.get_disk_size_by_sku(self.db,
                                                                         db_rsc_price.sku) * db_dim_temp.qty * 4
                ################################################################################
                # Add backup storage per VM
                ################################################################################
                vm_storage = 0
                for d in [x for x in lstAuxRsc if x.resource_type == "Storage" and x.vendor == "Azure"]:
                    vm_storage += self.dbAzureDiskSpecDict[d.sku]
                backupRatio = self.get_vm_backup_ratio(db_dim_temp)
                sku = "azure_backup_storage_gb"
                db_rsc_price = DbResourcePrice.get_by_region_sku(
                    self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
                db_detail = self.new_db_bom_from_price(
                    db_rsc_price=db_rsc_price,
                    env_type=env,
                    app_role=db_dim_temp.app_role,
                    qty=round(db_dim_temp.qty * vm_storage * backupRatio),
                    lv=BomLevel.SECONDARY,
                    bom_type=BomType.INFRA,
                    bom_subtype="Azure Servers"
                )
                lstAuxRsc.append(db_detail)
                ################################################################################
                # Add Azure shared services per VM
                ################################################################################
                sku = "azure_shared_service"
                db_rsc_price = DbResourcePrice.get_by_region_sku(
                    self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
                db_detail = self.new_db_bom_from_price(
                    db_rsc_price=db_rsc_price,
                    env_type=env,
                    app_role=db_dim_temp.app_role,
                    qty=db_dim_temp.qty,
                    lv=BomLevel.SECONDARY,
                    bom_type=BomType.INFRA,
                    bom_subtype="Azure Shared Services"
                )
                lstAuxRsc.append(db_detail)
                ################################################################################
                # Add Servers Software Licensing per VM
                ################################################################################
                if db_dim_temp.is_asr_required:
                    # ASR agent license
                    sku = "azure_asr_agent"
                    db_rsc_price = DbResourcePrice.get_by_region_sku(
                        self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.INFRA,
                        bom_subtype="Servers Software Licensing"
                    )
                    lstAuxRsc.append(db_detail)
                if OsType(db_dim_temp.os_type) == OsType.LINUX:
                    if LinuxDist(db_dim_temp.linux_dist) == LinuxDist.RHEL:
                        # RHEL licensing
                        sku = "lic_rhel"
                        db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                        db_detail = self.new_db_bom_from_price(
                            db_rsc_price=db_rsc_price,
                            env_type=env,
                            app_role=db_dim_temp.app_role,
                            qty=db_dim_temp.qty,
                            lv=BomLevel.SECONDARY,
                            bom_type=BomType.INFRA,
                            bom_subtype="Servers Software Licensing"
                        )
                        lstAuxRsc.append(db_detail)
                elif OsType(db_dim_temp.os_type) == OsType.WINDOWS:
                    # Add Cisco AMP licenses for Windows servers
                    sku = "csco_amp"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.INFRA,
                        bom_subtype="Servers Software Licensing"
                    )
                    lstAuxRsc.append(db_detail)
                    # add Shavlik/Ivanti Patch Management
                    sku = "si_patch_mgmt"
                    db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                    db_detail = self.new_db_bom_from_price(
                        db_rsc_price=db_rsc_price,
                        env_type=env,
                        app_role=db_dim_temp.app_role,
                        qty=db_dim_temp.qty,
                        lv=BomLevel.SECONDARY,
                        bom_type=BomType.INFRA,
                        bom_subtype="Servers Software Licensing"
                    )
                    lstAuxRsc.append(db_detail)
                ################################################################################
                # Add Managed Services per VM
                ################################################################################
                # Sys Eng Service Requests Packs (8 hrs p pack)
                sku = "sys_eng_sr_pack"
                db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                db_detail = self.new_db_bom_from_price(
                    db_rsc_price=db_rsc_price,
                    env_type=env,
                    app_role=db_dim_temp.app_role,
                    qty=db_dim_temp.qty,
                    lv=BomLevel.SECONDARY,
                    bom_type=BomType.LABOR,
                    bom_subtype="Managed Services"
                )
                lstAuxRsc.append(db_detail)
                # Initial VM Setup Fee
                if db_dim_temp.app_role == "Citrix" or db_dim_temp.app_role == "File Server":
                    sku = "labor_vm_1"
                else:
                    sku = "labor_vm_2"
                db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
                db_detail = self.new_db_bom_from_price(
                    db_rsc_price=db_rsc_price,
                    env_type=env,
                    app_role=db_dim_temp.app_role,
                    qty=db_dim_temp.qty,
                    lv=BomLevel.SECONDARY,
                    bom_type=BomType.LABOR,
                    bom_subtype="Managed Services"
                )
                # distribute the initial setup fee to the client's contract term
                db_detail.total_price /= self.dbSummaryRecords.contract_term
                lstAuxRsc.append(db_detail)

                ################################################################################
                # Combine VM BoM and auxiliary BoM
                ################################################################################
                self.dbDetailRecords[env] += lstAuxRsc

        ######################################################################
        # create shared BoM across environments
        ######################################################################

        ######################################################################
        # Add per client Azure Shared Services
        ######################################################################
        # Proportional usage of shared Active Directory
        sku = "azure_shared_ad"
        db_rsc_price = DbResourcePrice.get_by_region_sku(
            self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=1,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Azure Shared Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        ######################################################################
        # Add per client Server Software Licensing
        ######################################################################
        # Azure keyvault usage
        sku = "azure_kv"
        db_rsc_price = DbResourcePrice.get_by_region_sku(
            self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=8,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Servers Software Licensing"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        ######################################################################
        # Add per client Network Services
        ######################################################################
        # Azure WAF/DDoS Services
        sku = "azure_waf_ddos_gb"
        db_rsc_price = DbResourcePrice.get_by_region_sku(
            self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=self.dbSummaryRecords.total_reg_users + self.dbSummaryRecords.total_view_users,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Network Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        # Azure Network Internet EGRESS (OUT)
        sku = "azure_inet_egress_gb"
        db_rsc_price = DbResourcePrice.get_by_region_sku(
            self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=self.dbSummaryRecords.azure_fileshare_storage_gb * 0.1,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Network Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        # Azure Network Express Route EGRESS (OUT)
        sku = "azure_er_egress_gb"
        db_rsc_price = DbResourcePrice.get_by_region_sku(
            self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=self.dbSummaryRecords.azure_fileshare_storage_gb * 0.1,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.INFRA,
            bom_subtype="Network Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        ######################################################################
        # Add per client Power BI
        ######################################################################
        if self.dbSummaryRecords.has_power_bi:
            # Power BI Pro Users
            # currently the Power BI Pro licenses are paid by customer and will not be included in this estimation
            # sku = "azure_powerbi_pro"
            # db_rsc_price = DbResourcePrice.get_by_region_sku(
            #     self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            # db_detail = self.new_db_bom_from_price(
            #     db_rsc_price=db_rsc_price,
            #     env_type=CalyxEnv.SHARED,
            #     app_role="",
            #     qty=self.dbSummaryRecords.report_creators + self.dbSummaryRecords.super_users + self.dbSummaryRecords.standard_users,
            #     lv=BomLevel.PRIMARY,
            #     bom_type=BomType.INFRA,
            #     bom_subtype="Power BI"
            # )
            # self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # RACS Super Users
            sku = "racs_super_user"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=self.dbSummaryRecords.super_users * 6,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Power BI"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # RACS Standard Users
            # The standard users uses Power BI standard license and currently is paid by customer
            # therefore we don't include it in this estimation
            # sku = "racs_standard_user"
            # db_rsc_price = DbResourcePrice.get_by_region_sku(
            #     self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            # db_detail = self.new_db_bom_from_price(
            #     db_rsc_price=db_rsc_price,
            #     env_type=CalyxEnv.SHARED,
            #     app_role="",
            #     qty=self.dbSummaryRecords.standard_users,
            #     lv=BomLevel.PRIMARY,
            #     bom_type=BomType.INFRA,
            #     bom_subtype="Power BI"
            # )
            # self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Azure Data Factory
            sku = "azure_data_factory"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=1,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Power BI"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Azure SQL Database Compute (vCores)
            sku = "azure_sql_vcore"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=round(self.dbSummaryRecords.db_storage_gb / 512),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Power BI"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Azure SQL Database Storage (GB)
            sku = "azure_sql_storage_gb"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=self.dbSummaryRecords.db_storage_gb,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Power BI"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        ######################################################################
        # DaaS v2 is TBD
        ######################################################################
        # implementation TBD
        ######################################################################
        # Azure File Share
        ######################################################################
        if self.dbSummaryRecords.azure_fileshare_storage_gb > 0:
            dbRimTeeShirtSize = DbRimTeeShirtSize.get_by_size(self.db, self.tshirt_size)
            effectiveStorageGb = round(self.dbSummaryRecords.db_storage_gb * dbRimTeeShirtSize.azure_file_usage * 1.2)
            # Storage (Standard w LRS Redundancy)
            sku = "azure_storage_gb"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="Storage",
                qty=effectiveStorageGb,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Snapshots (Backup w/ Soft Delete)
            sku = "azure_storage_gb"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="Snapshots",
                qty=round(effectiveStorageGb * 0.9),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # SMB & REST Operations - Put, Create
            sku = "azure_rest_pcl"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="SMB & REST Operations - Put, Create",
                qty=math.ceil(effectiveStorageGb / 100),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # SMB & REST Operations - List
            sku = "azure_rest_pcl"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="SMB & REST Operations - List",
                qty=math.ceil(effectiveStorageGb / 100),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # SMB & REST Operations - Other
            sku = "azure_rest_other"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="SMB & REST Operations - Other",
                qty=math.ceil(effectiveStorageGb / 100),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Azure Defender for Storage
            sku = "azure_defender"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=3 * math.ceil(effectiveStorageGb / 100),
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Sync Servers
            sku = "fs_sync_server"
            db_rsc_price: DbResourcePrice = DbResourcePrice.get_by_sku(self.db, sku)
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=self.dbSummaryRecords.azure_fileshare_sync_servers,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
            # Outbound Data Transfer
            sku = "azure_out_data_gb"
            db_rsc_price = DbResourcePrice.get_by_region_sku(
                self.db, sku, CalyxRegion(self.dbSummaryRecords.azure_region))
            db_detail = self.new_db_bom_from_price(
                db_rsc_price=db_rsc_price,
                env_type=CalyxEnv.SHARED,
                app_role="",
                qty=self.dbSummaryRecords.azure_fileshare_sync_servers * self.dbSummaryRecords.db_storage_gb * dbRimTeeShirtSize.azure_file_usage * 1.2 * 0.1,
                lv=BomLevel.PRIMARY,
                bom_type=BomType.INFRA,
                bom_subtype="Azure File Share"
            )
            self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        ######################################################################
        # Managed Services
        ######################################################################
        # DR Testing & DRP maintenance
        sku = "dr_test"
        db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=1,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.LABOR,
            bom_subtype="Managed Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)
        # VM DR Setup & Storage Replication
        sku = "dr_setup"
        db_rsc_price = DbResourcePrice.get_by_sku(self.db, sku)
        db_detail = self.new_db_bom_from_price(
            db_rsc_price=db_rsc_price,
            env_type=CalyxEnv.SHARED,
            app_role="",
            qty=1,
            lv=BomLevel.PRIMARY,
            bom_type=BomType.LABOR,
            bom_subtype="Managed Services"
        )
        self.dbDetailRecords[CalyxEnv.SHARED].append(db_detail)

        ################################################################################
        # Adjust shared resources for multitenant clients
        ################################################################################
        if self.dbSummaryRecords.is_multitenant:
            # DB Servers
            for env in self.dbDetailRecords:
                for db_detail in [x for x in self.dbDetailRecords[env]
                                  if (x.app_role == "Database" or x.app_role == "Standby Database") and
                                     (x.bom_subtype == "Database Licensing" or
                                      x.bom_subtype == "Azure Servers")]:
                    db_detail.total_price *= self.dbSummaryRecords.multitenant_db_ratio
                    db_detail.remark = f'''Multitenant client shares {
                        self.dbSummaryRecords.multitenant_db_ratio * 100:.2f}% of the resource'''

        ################################################################################
        # Multiply the resource with number of environments
        ################################################################################
        for env in self.dbEnvRecords:
            if self.dbEnvRecords[env].qty > 1:
                for db_detail in self.dbDetailRecords[env]:
                    db_detail.qty *= self.dbEnvRecords[env].qty
                    db_detail.total_price *= self.dbEnvRecords[env].qty

        ################################################################################
        # Convert the currency to the target currency
        ################################################################################
        targetCurrency = self.get_target_currency()
        for env in self.dbEnvRecords:
            for db_detail in self.dbDetailRecords[env]:
                if db_detail.currency != targetCurrency.value:
                    rate = self.dbExchangeRateDict[Currency(db_detail.currency)] / self.dbExchangeRateDict[targetCurrency]
                    db_detail.unit_price *= rate
                    db_detail.total_price *= rate
                    db_detail.currency = targetCurrency.value

    def get_tshirt_size(self):
        """
        calculate the T-Shirt Size of the system, e.g. Small/Medium/Large/XLarge
        publish user counts the majority of the system usage
        assume the T-shirt size list is already sorted (ascend)
        """
        db_size = self.specIn.users.totalPublishUsers + \
            self.specIn.users.totalRegistrationUsers * 0.1 + \
            self.specIn.users.totalViewUsers * 0.1

        self.tshirt_size = TeeShirtSize.XLARGE
        for t in self.lst_tshirt_sizes:
            if db_size <= t.db_size_upper:
                self.tshirt_size = TeeShirtSize(t.tshirt_size)
                break

    def get_vm_backup_ratio(self, db_dim_temp: DimensionTemplate) -> float:
        env = CalyxEnv(db_dim_temp.env)
        if env is CalyxEnv.SHARED or env is CalyxEnv.PROD:
            env = CalyxEnv.PROD
        else:
            env = CalyxEnv.NONPROD
        serverBackupType = ServerBackupType(db_dim_temp.backup_type)
        d = self.dbBackupRatioDict[env][serverBackupType]
        fd = 1 - d[ServerBackupAction.FIRST_DEDUPE]
        fc = 1 - d[ServerBackupAction.FIRST_COMPRESS]
        od = 1 - d[ServerBackupAction.ONGOING_DEDUPE]
        oc = 1 - d[ServerBackupAction.ONGOING_COMPRESS]
        r = db_dim_temp.weekly_data_chg_rate
        if env is CalyxEnv.PROD:
            # PROD: initial import + 30 day change + 1 year change?
            ratio = fd * fc + od * oc * r / 7 * 30 + od * oc * r * 52
        else:
            # NONPROD: initial import + 14 weeks change?
            ratio = fd * fc + od * oc * r * 14
        return ratio

    @staticmethod
    def db_rim_summary_records_to_spec_in(db_rim: DbRimSummaryRecords) -> RimSpecIn:
        # Project Info
        rimSpec = RimSpecIn()
        # rimSpec.project.customer_name = db_rim.
        # rimSpec.project.project_name = db_rim.
        rimSpec.project.discount = db_rim.discount
        if db_rim.update_username is None:
            rimSpec.project.author = db_rim.create_username
        else:
            rimSpec.project.author = db_rim.update_username
        rimSpec.project.date = db_rim.update_date
        rimSpec.project.version = db_rim.version
        rimSpec.project.is_customized = db_rim.is_customized
        # RIM User Info
        rimSpec.users.totalRegistrationUsers = db_rim.total_reg_users
        rimSpec.users.concurrentRegistrationUsers = db_rim.conc_reg_users
        rimSpec.users.totalPublishUsers = db_rim.total_pub_users
        rimSpec.users.concurrentPublishUsers = db_rim.conc_pub_users
        rimSpec.users.totalViewUsers = db_rim.total_view_users
        rimSpec.users.concurrentViewUsers = db_rim.conc_view_users
        # RIM environments
        rimSpec.environments.nProdEnv = db_rim.prod_envs
        rimSpec.environments.nNonProdValidatedEnv = db_rim.nonprodval_envs
        rimSpec.environments.nNonProdEnv = db_rim.nonprod_envs
        # rimSpec.environments.prodEnvSharedRatio = db_rim.multitenant_db_ratio
        # rimSpec.environments.nonProdValidatedEnvSharedRatio = db_rim.multitenant_db_ratio
        # rimSpec.environments.nonProdEnvSharedRatio = db_rim.multitenant_db_ratio
        # Misc
        rimSpec.misc.isMultiTenant = db_rim.is_multitenant
        rimSpec.misc.multiTenantDbRatio = db_rim.multitenant_db_ratio
        rimSpec.misc.hasProdReadReplicaDatabase = db_rim.has_prod_read_replica_db
        rimSpec.misc.hasNonProdValReadReplicaDatabase = db_rim.has_nonprodval_read_replica_db
        rimSpec.misc.hasNonProdReadReplicaDatabase = db_rim.has_nonprod_read_replica_db
        rimSpec.misc.hasCitrix = db_rim.has_citrix
        rimSpec.misc.dbStorage = db_rim.db_storage_gb
        rimSpec.misc.azureRegion = db_rim.azure_region
        rimSpec.misc.contractTerm = db_rim.contract_term
        # Analytics (Power BI)
        rimSpec.analytics.hasPowerBi = db_rim.has_power_bi
        rimSpec.analytics.reportCreators = db_rim.report_creators
        rimSpec.analytics.superUsers = db_rim.super_users
        rimSpec.analytics.standardUser = db_rim.standard_users
        # Azure file share
        rimSpec.azureFileShare.azureFileShareStorage = db_rim.azure_fileshare_storage_gb
        rimSpec.azureFileShare.azureFilesShareSyncServers = db_rim.azure_fileshare_sync_servers
        # Internal parameters
        rimSpec.internal.useAzureRiRate = db_rim.has_azure_ri_discount
        rimSpec.internal.hasVendorDiscount = db_rim.has_vendor_discount
        rimSpec.internal.slaTarget = db_rim.sla
        rimSpec.internal.hasDisasterRecovery = db_rim.has_dr
        rimSpec.internal.drRpo = db_rim.dr_rpo
        rimSpec.internal.drRto = db_rim.dr_rto
        # return value
        return rimSpec
