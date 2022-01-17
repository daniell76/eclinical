<template>
    <div>
        <div class="crumbs">
            <el-breadcrumb separator="/">
                <el-breadcrumb-item>
                    <i class="el-icon-lx-cascades"></i> Resource Price Table
                </el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="container">
            <div class="handle-box">
                <el-select v-model="query.region" placeholder="Region" class="handle-select mr10">
                    <el-option key="1" label="All Regions" value="ALL"></el-option>
                    <el-option key="2" label="US EAST 2" value="US EAST 2"></el-option>
                    <el-option key="3" label="US CENTRAL" value="US CENTRAL"></el-option>
                    <el-option key="4" label="EU WEST" value="EU WEST"></el-option>
                    <el-option key="5" label="EU NORTH" value="EU NORTH"></el-option>
                    <el-option key="6" label="CN EAST 2" value="CN EAST 2"></el-option>
                    <el-option key="7" label="CN NORTH 2" value="CN NORTH 2"></el-option>
                    <el-option key="8" label="Not Specified" value="NONE"></el-option>
                </el-select>
                <el-select v-model="query.service_name" placeholder="Device Type" class="handle-select mr10">
                    <el-option key="1" label="All Types" value="ALL"></el-option>
                    <el-option key="2" label="VM" value="Virtual Machines"></el-option>
                    <el-option key="3" label="DISK" value="Storage"></el-option>
                    <el-option key="4" label="Others" value="OTHERS"></el-option>
                </el-select>
                <el-select v-model="query.currency" placeholder="Currency" class="handle-select mr10">
                    <el-option key="1" label="All" value="ALL"></el-option>
                    <el-option key="2" label="USD" value="USD"></el-option>
                    <el-option key="3" label="CNY" value="CNY"></el-option>
                </el-select>
                <el-input v-model="query.sku" placeholder="SKU" class="handle-input mr10"></el-input>
                <el-button type="primary" icon="el-icon-search" @click="handleSearch">Search</el-button>
            </div>
            <el-table :data="res.tableData" border class="table" ref="multipleTable" header-cell-class-name="table-header">
                <el-table-column prop="id" label="id" width="55" align="center"></el-table-column>
                <el-table-column prop="sku" label="sku"></el-table-column>
                <el-table-column prop="os_type" label="os type"></el-table-column>
                <el-table-column prop="currency" label="currency"></el-table-column>
                <el-table-column prop="unit_price" label="unit price"></el-table-column>
                <el-table-column prop="reservation_term" label="reservation term"></el-table-column>
                <el-table-column prop="azure_region" label="azure region"></el-table-column>
                <el-table-column prop="vendor" label="vendor"></el-table-column>
                <el-table-column prop="service_name" label="service name"></el-table-column>
                <el-table-column prop="description" label="description"></el-table-column>
<!--                <el-table-column prop="billing_type" label="billing_type"></el-table-column>
                <el-table-column prop="create_username" label="Created By"></el-table-column>
                <el-table-column prop="create_date" label="Created On"></el-table-column>
                <el-table-column prop="update_username" label="Changed By"></el-table-column>
                <el-table-column prop="update_date" label="Changed On"></el-table-column>
                <el-table-column label="Operation" width="180" align="center">
                    <template #default="scope">
                        <el-button type="text" icon="el-icon-edit" @click="handleEdit(scope.$index, scope.row)">Edit</el-button>
                        <el-button type="text" icon="el-icon-delete" class="red"
                            @click="handleDelete(scope.$index, scope.row)">Delete</el-button>
                    </template>
                </el-table-column> -->
            </el-table>
            <div class="pagination">
                <el-pagination background layout="total, prev, pager, next" :current-page="query.pageNum"
                    :page-size="query.pageSize" :total="res.pageTotal" @current-change="handlePageChange"></el-pagination>
            </div>
        </div>

        <!-- 编辑弹出框 -->
        <el-dialog title="Edit" v-model="editVisible" width="30%">
            <el-form label-width="70px">
                <el-table-column prop="sku" label="sku"></el-table-column>
                <el-table-column prop="os_type" label="os_type"></el-table-column>
                <el-table-column prop="currency" label="currency"></el-table-column>
                <el-table-column prop="unit_price" label="unit_price"></el-table-column>
                <el-table-column prop="reservation_term" label="reservation_term"></el-table-column>
                <el-table-column prop="azure_region" label="azure_region"></el-table-column>
                <el-table-column prop="vendor" label="vendor"></el-table-column>
                <el-table-column prop="service_name" label="service_name"></el-table-column>
                <el-table-column prop="description" label="description"></el-table-column>
                <el-table-column prop="billing_type" label="billing_type"></el-table-column>
                <el-form-item label="sku"><el-input v-model="editForm.sku"></el-input></el-form-item>
                <el-form-item label="os_type"><el-input v-model="editForm.os_type"></el-input></el-form-item>
                <el-form-item label="currency"><el-input v-model="editForm.currency"></el-input></el-form-item>
                <el-form-item label="unit_price"><el-input v-model="editForm.unit_price"></el-input></el-form-item>
                <el-form-item label="reservation_term"><el-input v-model="editForm.reservation_term"></el-input></el-form-item>
                <el-form-item label="azure_region"><el-input v-model="editForm.azure_region"></el-input></el-form-item>
                <el-form-item label="vendor"><el-input v-model="editForm.vendor"></el-input></el-form-item>
                <el-form-item label="service_name"><el-input v-model="editForm.service_name"></el-input></el-form-item>
                <el-form-item label="description"><el-input v-model="editForm.description"></el-input></el-form-item>
                <el-form-item label="billing_type"><el-input v-model="editForm.billing_type"></el-input></el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="editVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="saveEdit">Save</el-button>
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
import '../utils/request'
// import { fetchData } from "../api/index";

export default {
    name: "basetable",
    setup() {
        const { proxy } = getCurrentInstance();
        const query = reactive({
            region: "ALL",
            service_name: "ALL",
            currency: "ALL",
            sku: "",
            pageNum: 1,
            pageSize: 10,
        });
        const res = reactive({
            tableData: [],
            pageTotal: 0,
        });
        // 获取表格数据
        const getData = () => {
            let searchParams = {};
            switch (query.region) {
                case "ALL":
                    break;
                case "NONE":
                    searchParams.azure_region = "";
                    break;
                default:
                    searchParams.azure_region = query.region;
            };
            switch (query.service_name) {
                case "ALL":
                case "OTHERS":
                    break;
                default:
                    searchParams.service_name = query.service_name
            }
            switch (query.currency) {
                case "ALL":
                    break;
                default:
                    searchParams.currency = query.currency
            }
            if (query.sku != "") {
                searchParams.sku = query.sku;
            }
            searchParams.page_num = query.pageNum;
            searchParams.page_size = query.pageSize;
            proxy.$api.get('/admin/resources/count', {params: searchParams})
            .then( response => {
                // console.log(response);
                res.pageTotal = response.data.count;
                // console.log(res.pageTotal);
            });
            proxy.$api.get('/admin/resources', {params: searchParams})
            .then((response) => {
                // console.log(res);
                res.tableData = response.data;
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

        // 删除操作
        const handleDelete = (index) => {
            // 二次确认删除
            ElMessageBox.confirm("确定要删除吗？", "提示", {
                type: "warning",
            })
                .then(() => {
                    ElMessage.success("删除成功");
                    res.tableData.splice(index, 1);
                })
                .catch(() => {});
        };

        // 表格编辑时弹窗和保存
        const editVisible = ref(false);
        const editForm = reactive({
            id: "",
            sku: "",
            os_type: "",
            currency: "",
            unit_price: "",
            reservation_term: "",
            azure_region: "",
            vendor: "",
            service_name: "",
            description: "",
            billing_type:"",
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
            editVisible.value = true;
        };
        const saveEdit = () => {
            editVisible.value = false;
            ElMessage.success(`修改第 ${idx + 1} 行成功`);
            Object.keys(editForm).forEach((item) => {
                res.tableData[idx][item] = editForm[item];
            });
        };
        return {
            query,
            res,
            editVisible,
            editForm,
            handleSearch,
            handlePageChange,
            handleDelete,
            handleEdit,
            saveEdit,
        };
    },
};
</script>

<style scoped>
.handle-box {
    margin-bottom: 20px;
}

.handle-select {
    width: 120px;
}

.handle-input {
    width: 300px;
    display: inline-block;
}
.table {
    width: 100%;
    font-size: 14px;
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
</style>
