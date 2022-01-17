<template>
    <div>
        <div class="crumbs">
            <el-breadcrumb separator="/">
                <el-breadcrumb-item>
                    <i class="el-icon-lx-cascades"></i> RIM Project Summary
                </el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="container">
            <div class="handle-box">
                <el-select v-model="query.usertype" placeholder="User Type" class="handle-select mr10">
                    <el-option key="1" label="My Projects" value="ME"></el-option>
                    <el-option key="2" label="All Projects" value="ALL"></el-option>
                    <el-option key="3" label="Others" value="OTHERS"></el-option>
                </el-select>
                <el-input v-bind:disabled="query.usertype!=='OTHERS' " v-model="query.username" placeholder="User Name" class="handle-input mr10"></el-input>
                <el-button type="primary" icon="el-icon-search" @click="handleSearch">Search</el-button>
            </div>
            <div class="header-right">
                <el-button type="primary" icon="el-icon-plus" @click="handleNewRimProject">New Project</el-button>
            </div>
            <!--<el-table :data="res.tableData" border class="table" ref="multipleTable" header-cell-class-name="table-header">-->
            <el-table ref="rimSummaryTable" :data="res.tableData" show-overflow-tooltip border class="table" header-cell-class-name="table-header"
                      @expand-change="handleExpandChange" :expand-row-keys="expands" :row-key='getRowKeys'>
                <el-table-column type="expand">
                    <template #default="{ row }">
                        <div>
                            <el-select v-model="row.details.selVersion" placeholder="Versions" class="handle-select2 mr10" @change="selectVersion(row)">
                                <el-option v-for="item in row.details.versions" :key="item.version" :label="item.version+' (updated on '+item.update_date+')'" :value="item.version"></el-option>
                            </el-select>
                            <el-button type="text" icon="el-icon-document-delete" @click="handleVersionDelete(row)" class="header-right red">Delete Version</el-button>
                            <el-button type="text" icon="el-icon-document" @click="handleVersionCalculate(row)" class="header-right">ReCalculate Version</el-button>
                            <el-button type="text" icon="el-icon-edit" @click="handleVersionEdit(row)" class="header-right">Edit Version</el-button>
                            <!--<el-button type="text" icon="el-icon-document-add" @click="handleNewVersion(scope.$index, scope.row)" class="header-right">New Version</el-button>-->
                        </div>
                        <br>
                        <div v-if="row.details.spec">
                            <label v-if="row.details.spec.project.is_customized" class="red">This calculation is customized!</label>
                            <label v-if="row.details.spec.project.discount > 0" class="red">Overall discount {{row.details.spec.project.discount * 100}}% applied!</label>
                            <el-collapse>
                                <el-collapse-item title="Specification" v-if="row.details.spec">
                                    <el-form label-width="200px">
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Azure Region"><el-input disabled v-model="row.details.spec.misc.azureRegion"></el-input></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Contractor Term"><el-input disabled v-model.number="row.details.spec.misc.contractTerm"></el-input></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Total Registered Users"><label>{{ row.details.spec.users.totalRegistrationUsers }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Concurrent Registered Users"><label>{{ row.details.spec.users.concurrentRegistrationUsers }}</label></el-form-item></el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Total Publishing Users"><label>{{ row.details.spec.users.totalPublishUsers }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Concurrent Publishing Users"><label>{{ row.details.spec.users.concurrentPublishUsers }}</label></el-form-item></el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Total Viewing Users"><label>{{ row.details.spec.users.totalViewUsers }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Concurrent Viewing Users"><label>{{ row.details.spec.users.concurrentViewUsers }}</label></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="# of Prod. Env."><label>{{ row.details.spec.environments.nProdEnv }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="# of Validation Env."><label>{{ row.details.spec.environments.nNonProdValidatedEnv }}</label></el-form-item></el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="12"></el-col>
                                            <el-col :span="12"><el-form-item label="# of Non-Prod. Env."><label>{{ row.details.spec.environments.nNonProdEnv }}</label></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Multitenant"><el-checkbox disabled v-model="row.details.spec.misc.isMultiTenant"></el-checkbox></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Database Ratio"><label>{{ row.details.spec.misc.multiTenantDbRatio }}</label></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Prod. Read Replica DB"><el-checkbox disabled v-model="row.details.spec.misc.hasProdReadReplicaDatabase"></el-checkbox></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Valid. Read Replica DB"><el-checkbox disabled v-model="row.details.spec.misc.hasNonProdValReadReplicaDatabase"></el-checkbox></el-form-item></el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Database Size (GB)"><label>{{ row.details.spec.misc.dbStorage }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Non-Prod. Read Replica DB"><el-checkbox disabled v-model="row.details.spec.misc.hasNonProdReadReplicaDatabase"></el-checkbox></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Citrix"><el-checkbox disabled v-model="row.details.spec.misc.hasCitrix"></el-checkbox></el-form-item></el-col>
                                            <el-col :span="12"></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Power BI Report"><el-checkbox disabled v-model="row.details.spec.analytics.hasPowerBi"></el-checkbox></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="# of Report Creaters"><label>{{ row.details.spec.analytics.reportCreators }}</label></el-form-item></el-col>
                                        </el-row>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="# of Super Users"><label>{{ row.details.spec.analytics.superUsers }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="# of Standard Users"><label>{{ row.details.spec.analytics.standardUser }}</label></el-form-item></el-col>
                                        </el-row>
                                        <hr /><br>
                                        <el-row>
                                            <el-col :span="12"><el-form-item label="Azure FS Size (GB)"><label>{{ row.details.spec.azureFileShare.azureFileShareStorage }}</label></el-form-item></el-col>
                                            <el-col :span="12"><el-form-item label="Sync Servers"><label>{{ row.details.spec.azureFileShare.azureFilesShareSyncServers }}</label></el-form-item></el-col>
                                        </el-row>
                                    </el-form>
                                </el-collapse-item>
                                <el-collapse-item :title="'Commercial Breakdown (' + row.details.results.yearlySummaryCost.total + ')'" v-if="row.details.results.yearlySummaryCost">
                                    <el-form label-width="200px">
                                        <el-form-item label="Labor"><label>{{ row.details.results.yearlySummaryCost.labor }}</label></el-form-item>
                                        <el-form-item label="Infrastructure"><label>{{ row.details.results.yearlySummaryCost.infra }}</label></el-form-item>
                                        <el-form-item label="Software Licenses"><label>{{ row.details.results.yearlySummaryCost.licenses }}</label></el-form-item>
                                        <hr /><br>
                                        <el-form-item label="Total"><label>{{ row.details.results.yearlySummaryCost.total }}</label></el-form-item>
                                    </el-form>
                                </el-collapse-item>
                                <el-collapse-item :title="'Technical Breakdown (' + row.details.results.yearlyDetailCost.total + ')'">
                                    <el-form v-if="row.details.results.yearlyDetailCost" label-width="200px">
                                        <el-form-item label="Azure Servers (VMs)"><label>{{ row.details.results.yearlyDetailCost.azureServers }}</label></el-form-item>
                                        <el-form-item label="Azure Shared Services"><label>{{ row.details.results.yearlyDetailCost.azureSharedServices }}</label></el-form-item>
                                        <el-form-item label="Server Software Licensing"><label>{{ row.details.results.yearlyDetailCost.serverSoftwareLicensing }}</label></el-form-item>
                                        <el-form-item label="Backup Services"><label>{{ row.details.results.yearlyDetailCost.backupServices }}</label></el-form-item>
                                        <el-form-item label="Database Licensing"><label>{{ row.details.results.yearlyDetailCost.databaseLicensing }}</label></el-form-item>
                                        <el-form-item label="Azure Network Services"><label>{{ row.details.results.yearlyDetailCost.azureNetworkServices }}</label></el-form-item>
                                        <el-form-item label="Client Software Licensing"><label>{{ row.details.results.yearlyDetailCost.clientSoftwareLicensing }}</label></el-form-item>
                                        <el-form-item label="Power BI"><label>{{ row.details.results.yearlyDetailCost.azurePowerBi }}</label></el-form-item>
                                        <el-form-item label="Azure File Share"><label>{{ row.details.results.yearlyDetailCost.azureFileShare }}</label></el-form-item>
                                        <el-form-item label="Managed Services"><label>{{ row.details.results.yearlyDetailCost.managedServices }}</label></el-form-item>
                                        <hr /><br>
                                        <el-form-item label="Total"><label>{{ row.details.results.yearlyDetailCost.total }}</label></el-form-item>
                                    </el-form>
                                </el-collapse-item>
                                <el-collapse-item v-if="row.details.results.details" title="BOM Details">
                                    <el-table ref="rimDetailTable" :data="row.details.results.details" show-overflow-tooltip border :row-class-name="isBomExpand" class="table" header-cell-class-name="table-header">
                                        <el-table-column type="expand">
                                            <template #default="{ row }">
                                                <el-table :data="row.components" show-overflow-tooltip border header-cell-class-name="table-header">
                                                    <el-table-column prop="sku" label="SKU"></el-table-column>
                                                    <el-table-column prop="vendor" label="Vendor"></el-table-column>
                                                    <el-table-column prop="app_role" label="Role"></el-table-column>
                                                    <el-table-column prop="currency" label="Currency"></el-table-column>
                                                    <el-table-column prop="unit_price" label="Unit Price"></el-table-column>
                                                    <el-table-column prop="qty" label="Qty."></el-table-column>
                                                    <el-table-column prop="total_price" label="Total"></el-table-column>
                                                    <el-table-column prop="sum_total_price" label="Sum"></el-table-column>
                                                    <el-table-column prop="bom_type" label="Cat 1"></el-table-column>
                                                    <el-table-column prop="bom_subtype" label="Cat 2"></el-table-column>
                                                    <el-table-column prop="region" label="Region"></el-table-column>
                                                </el-table>
                                            </template>
                                        </el-table-column>
                                        <el-table-column prop="sku" label="SKU"></el-table-column>
                                        <el-table-column prop="vendor" label="Vendor"></el-table-column>
                                        <el-table-column prop="app_role" label="Role"></el-table-column>
                                        <el-table-column prop="currency" label="Currency"></el-table-column>
                                        <el-table-column prop="unit_price" label="Unit Price"></el-table-column>
                                        <el-table-column prop="qty" label="Qty."></el-table-column>
                                        <el-table-column prop="total_price" label="Total"></el-table-column>
                                        <el-table-column prop="sum_total_price" label="Sum"></el-table-column>
                                        <el-table-column prop="bom_type" label="Cat 1"></el-table-column>
                                        <el-table-column prop="bom_subtype" label="Cat 2"></el-table-column>
                                        <el-table-column prop="region" label="Region"></el-table-column>
                                        <el-table-column label="Operation" align="center">
                                            <template #default="{ row }">
                                                <el-button type="text" icon="el-icon-edit" @click="handleItemEdit(scope.$index, scope.row)">Edit</el-button>
                                                <el-button type="text" icon="el-icon-delete" class="red"
                                                           @click="handleItemDelete(scope.$index, scope.row)">Delete</el-button>
                                            </template>
                                        </el-table-column>
                                    </el-table>
                                </el-collapse-item>
                            </el-collapse>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column prop="uuid" label="Project ID" width="300" align="center"></el-table-column>
                <el-table-column prop="customer_name" label="Customer Name"></el-table-column>
                <el-table-column prop="project_name" label="Project Name"></el-table-column>
                <el-table-column prop="app" width="120" label="Application"></el-table-column>
                <el-table-column prop="remark" label="Description"></el-table-column>
                <el-table-column prop="update_date" label="Last Updated On"></el-table-column>
                <el-table-column prop="update_username" label="Updated By"></el-table-column>
                <el-table-column prop="create_username" label="Owner"></el-table-column>
                <el-table-column label="Operation" width="180" align="center">
                    <template #default="scope">
                        <el-button type="text" icon="el-icon-edit" @click="handleEdit(scope.$index, scope.row)">Edit</el-button>
                        <el-button type="text" icon="el-icon-delete" class="red"
                                   @click="handleProjDelete(scope.$index, scope.row)">Delete</el-button>
                    </template>
                </el-table-column> -->
            </el-table>
            <div class="pagination">
                <el-pagination background layout="total, prev, pager, next" :current-page="query.pageNum"
                               :page-size="query.pageSize" :total="res.pageTotal" @current-change="handlePageChange"></el-pagination>
            </div>
        </div>

        <!-- editor pop-up window -->
        <el-dialog title="Edit Project Summary" v-model="editVisible" width="30%">
            <el-form label-width="200px">
                <el-form-item label="Project ID"><label>{{ editForm.uuid }}</label></el-form-item>
                <el-form-item label="Customer Name"><el-input v-model="editForm.customer_name"></el-input></el-form-item>
                <el-form-item label="Project Name"><el-input v-model="editForm.project_name"></el-input></el-form-item>
                <el-form-item label="Application"><label>{{ editForm.app }}</label></el-form-item>
                <el-form-item label="Description"><el-input v-model="editForm.remark"></el-input></el-form-item>
                <el-form-item label="Owner"><label>{{ editForm.create_username }}</label></el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="editVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="saveEdit">Save</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- New RIM project pop-up window -->
        <el-dialog title="New RIM Project" v-model="newProjVisible" width="50%">
            <el-form label-width="200px">
                <el-row>
                    <el-col :span="12"><el-form-item label="Customer Name"><el-input v-model="newProjForm.customer_name"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Project Name"><el-input v-model="newProjForm.project_name"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <el-form-item label="Region">
                            <el-select v-model="newProjForm.azure_region" placeholder="Region" class="handle-select mr10">
                                <el-option key="1" label="United States" value="US"></el-option>
                                <el-option key="2" label="Europe" value="EU"></el-option>
                                <el-option key="3" label="China" value="CN"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="Contract Term">
                            <el-select v-model.number="newProjForm.contract_term" placeholder="contract term" class="handle-select mr10">
                                <el-option key="1" label="1 Year" :value="1"></el-option>
                                <el-option key="2" label="3 Years" :value="3"></el-option>
                                <el-option key="3" label="5 Years" :value="5"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Registered Users"><el-input v-model.number="newProjForm.total_reg_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Registered Users"><el-input v-model.number="newProjForm.conc_reg_users"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Publishing Users"><el-input v-model.number="newProjForm.total_pub_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Publishing Users"><el-input v-model.number="newProjForm.conc_pub_users"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Viewing Users"><el-input v-model.number="newProjForm.total_view_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Viewing Users"><el-input v-model.number="newProjForm.conc_view_users"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="# of Prod. Env."><el-input v-model.number="newProjForm.prod_envs"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Validation Env."><el-input v-model.number="newProjForm.nonprodval_envs"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"></el-col>
                    <el-col :span="12"><el-form-item label="# of Non-Prod. Env."><el-input v-model.number="newProjForm.nonprod_envs"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Multitenant"><el-checkbox v-model="newProjForm.is_multitenant"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Database Ratio"><el-input :disabled="!newProjForm.is_multitenant" v-model.number="newProjForm.multitenant_db_ratio"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Prod. Read Replica DB"><el-checkbox v-model="newProjForm.has_prod_read_replica_db"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Valid. Read Replica DB"><el-checkbox v-model="newProjForm.has_nonprodval_read_replica_db"></el-checkbox></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Database Size (GB)"><el-input v-model.number="newProjForm.db_storage_gb"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Non-Prod. Read Replica DB"><el-checkbox v-model="newProjForm.has_nonprod_read_replica_db"></el-checkbox></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Citrix"><el-checkbox v-model="newProjForm.has_citrix"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Power BI Report"><el-checkbox v-model="newProjForm.has_power_bi"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Report Creaters"><el-input :disabled="!newProjForm.has_power_bi" v-model.number="newProjForm.report_creators"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="# of Super Users"><el-input :disabled="!newProjForm.has_power_bi" v-model.number="newProjForm.super_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Standard Users"><el-input :disabled="!newProjForm.has_power_bi" v-model.number="newProjForm.standard_users"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Azure FS Size (GB)"><el-input v-model.number="newProjForm.azure_fileshare_storage_gb"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Sync Servers"><el-input v-model.number="newProjForm.azure_fileshare_sync_servers"></el-input></el-form-item></el-col>
                </el-row>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="newProjVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="confirmNewRimProject">Create</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- New/Edit version pop-up window -->
        <el-dialog :title="'New/Edit RIM Project Version (Project ID: ' + editVersionForm.uuid + ', Version: ' + editVersionForm.current_version + ')'" v-model="editVersionVisible" width="50%">
            <el-form label-width="200px">
                <el-row>
                    <el-col :span="12"><el-form-item label="Customer Name"><el-input disabled v-model="editVersionForm.customer_name"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Project Name"><el-input disabled v-model="editVersionForm.project_name"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12">
                        <el-form-item label="Region">
                            <el-select disabled v-model="editVersionForm.azure_region" placeholder="Region" class="handle-select mr10">
                                <el-option key="1" label="United States" value="US"></el-option>
                                <el-option key="2" label="Europe" value="EU"></el-option>
                                <el-option key="3" label="China" value="CN"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="Contract Term">
                            <el-select v-model.number="editVersionForm.contract_term" placeholder="contract term" class="handle-select mr10">
                                <el-option key="1" label="1 Year" :value="1"></el-option>
                                <el-option key="2" label="3 Years" :value="3"></el-option>
                                <el-option key="3" label="5 Years" :value="5"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Registered Users"><el-input v-model.number="editVersionForm.total_reg_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Registered Users"><el-input v-model.number="editVersionForm.conc_reg_users"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Publishing Users"><el-input v-model.number="editVersionForm.total_pub_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Publishing Users"><el-input v-model.number="editVersionForm.conc_pub_users"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Total Viewing Users"><el-input v-model.number="editVersionForm.total_view_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Concurrent Viewing Users"><el-input v-model.number="editVersionForm.conc_view_users"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="# of Prod. Env."><el-input v-model.number="editVersionForm.prod_envs"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Validation Env."><el-input v-model.number="editVersionForm.nonprodval_envs"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"></el-col>
                    <el-col :span="12"><el-form-item label="# of Non-Prod. Env."><el-input v-model.number="editVersionForm.nonprod_envs"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Multitenant"><el-checkbox v-model="editVersionForm.is_multitenant"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Database Ratio"><el-input :disabled="!editVersionForm.is_multitenant" v-model.number="editVersionForm.multitenant_db_ratio"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Prod. Read Replica DB"><el-checkbox v-model="editVersionForm.has_prod_read_replica_db"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Valid. Read Replica DB"><el-checkbox v-model="editVersionForm.has_nonprodval_read_replica_db"></el-checkbox></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="Database Size (GB)"><el-input v-model.number="editVersionForm.db_storage_gb"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Non-Prod. Read Replica DB"><el-checkbox v-model="editVersionForm.has_nonprod_read_replica_db"></el-checkbox></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Citrix"><el-checkbox v-model="editVersionForm.has_citrix"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Power BI Report"><el-checkbox v-model="editVersionForm.has_power_bi"></el-checkbox></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Report Creaters"><el-input :disabled="!editVersionForm.has_power_bi" v-model.number="editVersionForm.report_creators"></el-input></el-form-item></el-col>
                </el-row>
                <el-row>
                    <el-col :span="12"><el-form-item label="# of Super Users"><el-input :disabled="!editVersionForm.has_power_bi" v-model.number="editVersionForm.super_users"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="# of Standard Users"><el-input :disabled="!editVersionForm.has_power_bi" v-model.number="editVersionForm.standard_users"></el-input></el-form-item></el-col>
                </el-row>
                <hr /><br>
                <el-row>
                    <el-col :span="12"><el-form-item label="Azure FS Size (GB)"><el-input v-model.number="editVersionForm.azure_fileshare_storage_gb"></el-input></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Sync Servers"><el-input v-model.number="editVersionForm.azure_fileshare_sync_servers"></el-input></el-form-item></el-col>
                </el-row>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="editVersionVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="confirmEditRimVersion">Save</el-button>
                    <el-button type="primary" @click="confirmNewRimVersion">Save as New Version</el-button>
                </span>
            </template>
        </el-dialog>

        <!-- Recalculate version pop-up window -->
        <el-dialog title="Confirm to Recalculate Project" v-model="recalcVisible" width="30%">
            <el-form label-width="200px">
                <el-form-item label="Project ID"><label>{{ recalcForm.uuid }}</label></el-form-item>
                <el-form-item label="Version"><label>{{ recalcForm.version }}</label></el-form-item>
                <el-form-item label="Customized"><el-checkbox disabled v-model="recalcForm.is_customized"></el-checkbox></el-form-item>
                <el-form-item label="Regenerate BOM List"><el-checkbox v-model="recalcForm.recreate_bom"></el-checkbox></el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="recalcVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="confirmVersionCalculate">Recalculate</el-button>
                </span>
            </template>
        </el-dialog>

    </div>
</template>

<script>
import { ref, reactive, getCurrentInstance } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import '../utils/request';
// import { fetchData } from "../api/index";

export default {
    name: "RIM Project Summaries",
    setup() {
        const { proxy } = getCurrentInstance();
        const router = useRouter();
        const query = reactive({
            usertype: "ALL",
            username: "",
            pageNum: 1,
            pageSize: 10,
        });
        const res = reactive({
            tableData: [],
            pageTotal: 0,
        });
        const newProjectRes = reactive({});
        const expands = reactive([]);
        const getRowKeys = (row) => {
            return row.uuid
        };
        // 获取表格数据
        const getData = () => {
            let searchParams = {};
            switch (query.usertype) {
                case "ME":
                    searchParams.create_username = localStorage.getItem("ms_username");
                    break;
                case "ALL":
                    break;
                case "OTHERS":
                    if (query.username != "") {
                        searchParams.create_username = query.username;
                    };
                    break;
            };
            searchParams.page_num = query.pageNum;
            searchParams.page_size = query.pageSize;
            proxy.$api.get('/rim/projects/count', {params: searchParams})
            .then( response => {
                // console.log(response);
                res.pageTotal = response.data.count;
                // console.log(res.pageTotal);
            });
            proxy.$api.get('/rim/projects', {params: searchParams})
            .then((response) => {
                response.data.map(item => {
                    item.details = {};
                });
                res.tableData = response.data;
                //console.log(res);
            });
        };
        // getData();

        // 查询操作
        const handleSearch = () => {
            query.pageNum = 1;
            getData();
        };
        // 分页导航
        const handlePageChange = (val) => {
            query.pageNum = val;
            getData();
        };

        // 表格编辑时弹窗和保存
        const editVisible = ref(false);
        const editForm = reactive({
            id: "",
            uuid: "",
            customer_name: "",
            project_name: "",
            app: "",
            remark: "",
            create_username: "",
            create_date: "",
            update_username: "", 
            update_date: "",
        });
        let idx = -1;
        const handleEdit = (index, row) => {
            idx = index;
            Object.keys(editForm).forEach((item) => {
                editForm[item] = row[item];
            });
            editForm["update_username"] = localStorage.getItem("ms_username");
            editVisible.value = true;
        };
        const saveEdit = () => {
            editVisible.value = false;
            // ElMessage.success(`修改第 ${idx + 1} 行成功`);
            proxy.$api.put('/rim/project/'+editForm.uuid, editForm)
            .then((response) => {
                ElMessage.success('Project '+editForm.uuid+' modified');
                handleSearch();
            });
        };
        
        // 新建项目编辑时弹窗和保存
        const newProjVisible = ref(false);
        const newProjForm = reactive({
            customer_name: "",
            project_name: "",
            discount: 0,
            total_reg_users: 0,
            conc_reg_users: 0,
            total_pub_users: 0,
            conc_pub_users: 0,
            total_view_users: 0,
            conc_view_users: 0,
            prod_envs: 1,
            nonprodval_envs: 0,
            nonprod_envs: 0,
            is_multitenant: false,
            multitenant_db_ratio: 0.0625,
            has_prod_read_replica_db: true,
            has_nonprodval_read_replica_db: false,
            has_nonprod_read_replica_db: false,
            has_citrix: true,
            db_storage_gb: 512,
            azure_region: "CN",  // US, EU, CN
            // currency: "CNY",  // USD, CNY
            contract_term: 3,  // 1, 3, or 5 years
            has_power_bi: false,// YES, NO
            report_creators: 0,
            super_users: 0,
            standard_users: 0,
            azure_fileshare_storage_gb: 0,
            azure_fileshare_sync_servers: 1,
        });
        const handleNewRimProject = () => {
            newProjVisible.value = true;
        };
        const confirmNewRimProject = () => {
            //let newProjParams = {
            //    "project": {
            //        "customer_name": newProjForm.customer_name,
            //        "project_name": newProjForm.project_name,
            //        "discount": newProjForm.discount,
            //    },
            //    "users": {
            //        "totalRegistrationUsers": newProjForm.total_reg_users,
            //        "concurrentRegistrationUsers": newProjForm.conc_reg_users,
            //        "totalPublishUsers": newProjForm.total_pub_users,
            //        "concurrentPublishUsers": newProjForm.conc_pub_users,
            //        "totalViewUsers": newProjForm.total_view_users,
            //        "concurrentViewUsers": newProjForm.conc_view_users
            //    },
            //    "environments": {
            //        "nProdEnv": newProjForm.prod_envs,
            //        "nNonProdValidatedEnv": newProjForm.nonprodval_envs,
            //        "nNonProdEnv": newProjForm.nonprod_envs,
            //    },
            //    "misc": {
            //        "isMultiTenant": newProjForm.is_multitenant,
            //        "multiTenantDbRatio": newProjForm.multitenant_db_ratio,
            //        "hasProdReadReplicaDatabase": newProjForm.has_prod_read_replica_db,
            //        "hasNonProdValReadReplicaDatabase": newProjForm.has_nonprodval_read_replica_db,
            //        "hasNonProdReadReplicaDatabase": newProjForm.has_nonprod_read_replica_db,
            //        "hasCitrix": newProjForm.has_citrix,
            //        "dbStorage": newProjForm.db_storage_gb,
            //        "azureRegion": newProjForm.azure_region,
            //        "contractTerm": newProjForm.contract_term
            //    },
            //    "analytics": {
            //        "hasPowerBi": newProjForm.has_power_bi,
            //        "reportCreators": newProjForm.report_creators,
            //        "superUsers": newProjForm.standard_users,
            //        "standardUser": newProjForm.standard_users
            //    },
            //    "azureFileShare": {
            //        "azureFileShareStorage": newProjForm.azure_fileshare_storage_gb,
            //        "azureFilesShareSyncServers": newProjForm.azure_fileshare_sync_servers
            //    }
            //}
            let newProjParams = form2spec(newProjForm);
            proxy.$api.post('/rim/project/new_project', newProjParams)
            .then((response) => {
                // console.log(res);
                // res.tableData = response.data;
                newProjVisible.value = false;
                ElMessage.success(`new project ` + response.data.projInfo.projId + ` created`);
                // console.log(response.data);
                // console.log(response.data.projInfo.projId);
                //localStorage.setItem("rim_expanded_projid", response.data.projInfo.projId);
            }).then((response) => {
                // query.pageNum = 1;
                // getData();
                // router.push("/RimProjDetail");
                handleSearch();
            });
        };
        // 项目删除操作
        const handleProjDelete = (index, row) => {
            // 二次确认删除
            ElMessageBox.confirm("Confirm to delete all verions of project " + row.uuid + "?", "Warning", { type: "warning" }
            ).then(() => {
                idx = index;
                Object.keys(editForm).forEach((item) => {
                    editForm[item] = row[item];
                });
                proxy.$api.delete('/rim/project/' + editForm.uuid
                ).then((response) => {
                    ElMessage.success("project " + editForm.uuid + " delete successfully");
                    handleSearch();
                });
            });
        };

        // 展开项目明细，一次只展开一行
        const handleExpandChange = (row, expandedRows) => {
            if (expandedRows.length >= 1) {
                let $table = proxy.$refs.rimSummaryTable;
                expands.splice(0);
                for (let i = 0; i < expandedRows.length; i++) {
                    if (getRowKeys(expandedRows[i]) == getRowKeys(row)) {
                        let uuid = getRowKeys(row);
                        let td = JSON.parse(JSON.stringify(res.tableData));
                        proxy.$api.get('/rim/project/' + uuid + '/versions'
                        ).then((response) => {
                            if (response.data.length > 0) {
                                let idx = res.tableData.indexOf(expandedRows[i]);
                                let ver = response.data[0].version;
                                td[idx].details.versions = response.data;
                                td[idx].details.selVersion = ver;
                                proxy.$api.get('/rim/project/' + uuid + '/spec', { params: {version: ver} }
                                ).then((specRes) => {
                                    td[idx].details.spec = specRes.data;
                                    proxy.$api.get('/rim/project/' + uuid, { params: { version: ver, detail: true } }
                                    ).then(verRes => {
                                        td[idx].details.results = verRes.data;
                                        res.tableData = td;
                                        expands.push(getRowKeys(row));
                                    });
                                });
                            };
                        });
                    }
                    //else {
                    //    $table.toggleRowExpansion(expandedRows[i]);
                    //};
                };
            };
        };

        // 本行是否需要展开
        const isBomExpand = (row, index) => {
            if (row.components === undefined || row.components === null || row.components.length <= 0) {
                return 'hide-expand'
            }
            return ''
        };

        // 加载新的项目版本
        const selectVersion = (row) => {
            if (row.details.selVersion) {
                if (row.details.spec.project.version && row.details.selVersion == row.details.spec.project.version) {
                } else {
                    loadProjectVersion(row.uuid, row.details.selVersion);
                }
            };
        };

        // 项目数据转换
        const form2spec = (form) => {
            let specParams = {
                "project": {
                    "customer_name": form.customer_name,
                    "project_name": form.project_name,
                    "discount": form.discount,
                },
                "users": {
                    "totalRegistrationUsers": form.total_reg_users,
                    "concurrentRegistrationUsers": form.conc_reg_users,
                    "totalPublishUsers": form.total_pub_users,
                    "concurrentPublishUsers": form.conc_pub_users,
                    "totalViewUsers": form.total_view_users,
                    "concurrentViewUsers": form.conc_view_users
                },
                "environments": {
                    "nProdEnv": form.prod_envs,
                    "nNonProdValidatedEnv": form.nonprodval_envs,
                    "nNonProdEnv": form.nonprod_envs,
                },
                "misc": {
                    "isMultiTenant": form.is_multitenant,
                    "multiTenantDbRatio": form.multitenant_db_ratio,
                    "hasProdReadReplicaDatabase": form.has_prod_read_replica_db,
                    "hasNonProdValReadReplicaDatabase": form.has_nonprodval_read_replica_db,
                    "hasNonProdReadReplicaDatabase": form.has_nonprod_read_replica_db,
                    "hasCitrix": form.has_citrix,
                    "dbStorage": form.db_storage_gb,
                    "azureRegion": form.azure_region,
                    "contractTerm": form.contract_term
                },
                "analytics": {
                    "hasPowerBi": form.has_power_bi,
                    "reportCreators": form.report_creators,
                    "superUsers": form.standard_users,
                    "standardUser": form.standard_users
                },
                "azureFileShare": {
                    "azureFileShareStorage": form.azure_fileshare_storage_gb,
                    "azureFilesShareSyncServers": form.azure_fileshare_sync_servers
                }
            }
            return specParams
        }
        // 编辑/创建新的项目版本
        const editVersionVisible = ref(false);
        const editVersionForm = reactive({});
        const handleVersionEdit = (row) => {

            editVersionForm.customer_name = row.details.spec.project.customer_name;
            editVersionForm.project_name = row.details.spec.project.project_name;
            editVersionForm.discount = row.details.spec.project.discount;
            editVersionForm.total_reg_users = row.details.spec.users.totalRegistrationUsers;
            editVersionForm.conc_reg_users = row.details.spec.users.concurrentRegistrationUsers;
            editVersionForm.total_pub_users = row.details.spec.users.totalPublishUsers;
            editVersionForm.conc_pub_users = row.details.spec.users.concurrentPublishUsers;
            editVersionForm.total_view_users = row.details.spec.users.totalViewUsers;
            editVersionForm.conc_view_users = row.details.spec.users.concurrentViewUsers;
            editVersionForm.prod_envs = row.details.spec.environments.nProdEnv;
            editVersionForm.nonprodval_envs = row.details.spec.environments.nNonProdValidatedEnv;
            editVersionForm.nonprod_envs = row.details.spec.environments.nNonProdEnv;
            editVersionForm.is_multitenant = row.details.spec.misc.isMultiTenant;
            editVersionForm.multitenant_db_ratio = row.details.spec.misc.multiTenantDbRatio;
            editVersionForm.has_prod_read_replica_db = row.details.spec.misc.hasProdReadReplicaDatabase;
            editVersionForm.has_nonprodval_read_replica_db = row.details.spec.misc.hasNonProdValReadReplicaDatabase;
            editVersionForm.has_nonprod_read_replica_db = row.details.spec.misc.hasNonProdReadReplicaDatabase;
            editVersionForm.has_citrix = row.details.spec.misc.hasCitrix;
            editVersionForm.db_storage_gb = row.details.spec.misc.dbStorage;
            editVersionForm.azure_region = row.details.spec.misc.azureRegion;
            editVersionForm.contract_term = row.details.spec.misc.contractTerm;
            editVersionForm.has_power_bi = row.details.spec.analytics.hasPowerBi;
            editVersionForm.report_creators = row.details.spec.analytics.reportCreators;
            editVersionForm.super_users = row.details.spec.analytics.superUsers;
            editVersionForm.standard_users = row.details.spec.analytics.standardUser;
            editVersionForm.azure_fileshare_storage_gb = row.details.spec.azureFileShare.azureFileShareStorage;
            editVersionForm.azure_fileshare_sync_servers = row.details.spec.azureFileShare.azureFilesShareSyncServers;

            editVersionForm.uuid = row.uuid;
            editVersionForm.current_version = row.details.selVersion;

            editVersionVisible.value = true;
        };
        const confirmEditRimVersion = () => {
            proxy.$api.put('/rim/project/' + editVersionForm.uuid + '/' + editVersionForm.current_version, form2spec(editVersionForm)
            ).then((verRes) => {
                editVersionVisible.value = false;
                refreshProjectData(editVersionForm.uuid);
            });
        };
        const confirmNewRimVersion = () => {
            proxy.$api.post('/rim/project/' + editVersionForm.uuid + '/new_version', form2spec(editVersionForm)
            ).then((verRes) => {
                editVersionVisible.value = false;
                refreshProjectData(editVersionForm.uuid);
            });
        };

        const handleVersionDelete = (row) => {
            // 二次确认删除
            ElMessageBox.confirm("Confirm to delete verion " + row.details.selVersion + "?", "Warning", { type: "warning" }
            ).then(() => {
                proxy.$api.delete('/rim/project/' + row.uuid + '/' + row.details.selVersion
                ).then((response) => {
                    ElMessage.success("Version " + row.details.selVersion + " delete successfully");
                    expands.splice(0);
                    handleSearch();
                });
            });
        };

        // 重新计算此项目版本
        const recalcVisible = ref(false);
        const recalcForm = reactive({});
        const handleVersionCalculate = (row) => {
            recalcForm.uuid = row.uuid;
            recalcForm.version = row.details.selVersion;
            recalcForm.is_customized = row.details.spec.project.is_customized;
            if (recalcForm.is_customized) {
                recalcForm.recreate_bom = false;
            } else {
                recalcForm.recreate_bom = true;
            };
            recalcVisible.value = true;
        };
        const confirmVersionCalculate = () => {
            let calcParams = {
                "version": recalcForm.version,
                "recreate_bom": recalcForm.is_customized,
                "detail": true
            };
            proxy.$api.post('/rim/project/' + recalcForm.uuid + '/calculate', calcParams
            ).then((calcRes) => {
                refreshProjectData(recalcForm.uuid);
            });
            recalcVisible.value = false;
        };
        const refreshProjectData = (uuid) => {
            let $table = proxy.$refs.rimSummaryTable.data;
            for (let i = 0; i < $table.length; i++) {
                if ($table[i].uuid == uuid) {
                    handleExpandChange($table[i], [$table[i]]);
                    break;
                }
            }
        };
        const loadProjectVersion = (uuid, version) => {
            let td = JSON.parse(JSON.stringify(res.tableData));
            let idx = -1;
            for (let i = 0; i < td.length; i++) {
                if (td[i].uuid == uuid) {
                    idx = i;
                    break;
                };
            }
            if (idx < 0) { return };
            proxy.$api.get('/rim/project/' + uuid + '/versions'
            ).then((response) => {
                if (response.data.length > 0) {
                    proxy.$api.get('/rim/project/' + uuid + '/spec', { params: { version: version } }
                    ).then((specRes) => {
                        td[idx].details.spec = specRes.data;
                        proxy.$api.get('/rim/project/' + uuid, { params: { version: version, detail: true } }
                        ).then(verRes => {
                            td[idx].details.results = verRes.data;
                            res.tableData = td;
                        });
                    });
                };
            });
        };
        return {
            query,
            res,
            newProjectRes,
            editVisible,
            editForm,
            handleSearch,
            handlePageChange,
            handleProjDelete,
            handleEdit,
            saveEdit,
            newProjVisible,
            newProjForm,
            handleNewRimProject,
            confirmNewRimProject,
            handleExpandChange,
            expands,
            getRowKeys,
            isBomExpand,
            selectVersion,
            editVersionVisible,
            editVersionForm,
            handleVersionEdit,
            confirmEditRimVersion,
            confirmNewRimVersion,
            handleVersionDelete,
            recalcVisible,
            recalcForm,
            handleVersionCalculate,
            confirmVersionCalculate,
            form2spec,
            refreshProjectData,
            loadProjectVersion
        };
    },
};
</script>

<style scoped>
.header-right {
    float: right;
    padding-right: 20px;
}
.handle-box {
    float: left;
    margin-bottom: 20px;
}
.handle-select {
    width: 120px;
}
.handle-select2 {
    width: 300px;
}
.handle-input {
    width: 300px;
    display: inline-block;
}
.table {
    width: 100%;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.red {
    color: #ff0000;
}
.mr10 {
    margin-right: 10px;
}
.table-td-thumb {
    display: block;
    margin: auto;
    width: 40px;
    height: 40px;
}
.form-border {
    border: solid 1px;
    border-radius: 20px;
    margin: 30px;
}
.form-shadow {
    box-shadow: 12px 12px 12px rgba(0,0,0,0.1);
}
.hide-expand {
    display: none
}
</style>
