<template>
    <div>
        <div class="crumbs">
            <el-breadcrumb separator="/">
                <el-breadcrumb-item>
                    <i class="el-icon-lx-cascades"></i> User Management 
                </el-breadcrumb-item>
            </el-breadcrumb>
        </div>
        <div class="container">
            <div class="handle-box">
                <el-select v-model="query.role" placeholder="Role" class="handle-select mr10">
                    <el-option key="1" label="All Users" value="ALL"></el-option>
                    <el-option key="2" label="Regular" value="USER"></el-option>
                    <el-option key="3" label="Admin" value="ADMIN"></el-option>
                </el-select>
                <el-select v-model="query.active" placeholder="Active" class="handle-select mr10">
                    <el-option key="1" label="All" value="ALL"></el-option>
                    <el-option key="2" label="Active" value="true"></el-option>
                    <el-option key="3" label="Disabled" value="false"></el-option>
                </el-select>
                <el-input v-model="query.username" placeholder="Username" class="handle-input mr10"></el-input>
                <el-button type="primary" icon="el-icon-search" @click="handleSearch">Search</el-button>
            </div>
            <el-table :data="res.tableData" border class="table" ref="multipleTable" header-cell-class-name="table-header">
                <el-table-column prop="id" label="id" width="55" align="center"></el-table-column>
                <el-table-column prop="username" label="User Name"></el-table-column>
                <el-table-column prop="role" label="Role"></el-table-column>
                <el-table-column prop="active" label="Active"></el-table-column>
                <!-- <el-table-column prop="login_time" :formatter="timeStampFormatter" label="Last Login"></el-table-column> -->
                <el-table-column prop="login_time" label="Last Login"></el-table-column>
              <el-table-column label="Operation" width="180" align="center">
                    <template #default="scope">
                        <el-button type="text" icon="el-icon-edit" @click="handleEdit(scope.$index, scope.row)">Edit</el-button>
                        <el-button type="text" icon="el-icon-delete" class="red"
                            @click="handleDelete(scope.$index, scope.row)">Delete</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <div class="pagination">
                <el-pagination background layout="total, prev, pager, next" :current-page="query.pageNum"
                    :page-size="query.pageSize" :total="res.pageTotal" @current-change="handlePageChange"></el-pagination>
            </div>
        </div>

        <!-- 编辑弹出框 -->
      <el-dialog title="Edit" v-model="editVisible" width="30%">
           <el-form :model="editForm" :rules="editFormRules" ref="editUser" label-width="160px">
                <el-form-item label="id"><label>{{ editForm.id }}</label></el-form-item>
                <el-form-item label="User Name"><label></label>{{ editForm.username }}</el-form-item>
                <el-form-item label="Password"><el-input v-model="editForm.password"></el-input></el-form-item>
                <el-form-item label="Confirm password"><el-input v-model="editForm.password2"></el-input></el-form-item>
                <el-form-item label="Role">
                    <el-select v-model="editForm.role" placeholder="Role" class="handle-select mr10">
                        <el-option key="1" label="Regular" value="USER"></el-option>
                        <el-option key="2" label="Admin" value="ADMIN"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="Active">
                    <el-select v-model="editForm.active" placeholder="Active" class="handle-select mr10">
                        <el-option key="1" label="true" value="true"></el-option>
                        <el-option key="2" label="false" value="false"></el-option>
                    </el-select>
                </el-form-item>
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
            role: "ALL",
            active: "ALL",
            username: "",
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
            switch (query.role) {
                case "ALL":
                    break;
                default:
                    searchParams.role = query.role;
            };
            switch (query.active) {
                case "ALL":
                    break;
                case "true":
                    searchParams.active = 1;
                    break;
                case "false":
                    searchParams.active = 0;
                    break;
            }
            if (query.username != "") {
                searchParams.username = query.username;
            }
            searchParams.page_num = query.pageNum;
            searchParams.page_size = query.pageSize;
            proxy.$api.get('/admin/users/count', {params: searchParams})
            .then( response => {
                // console.log(response);
                res.pageTotal = response.data.count;
                // console.log(res.pageTotal);
            });
            proxy.$api.get('/admin/users', {params: searchParams})
            .then((response) => {
                // console.log(res);
                res.tableData = response.data;
                for (var i = 0; i < res.tableData.length; i++) {
                    res.tableData[i].login_time = new Date(res.tableData[i].login_time * 1000).toLocaleString();
                }
            });
        };

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
        const editUser = ref(null);
        const editVisible = ref(false);
        const chkPwEqual = (rule, value, callback) => {
            if (reg_param.password === value) {
                callback()
            } else {
                callback(new Error("Password does not match!"))
            }
        };
        const editFormRules = {
            password: [
                { required: true, message: "Please set your password", trigger: "blur" },
                { min: 3, message: "at least 3 charecters", trigger: "blur" }
            ],
            password2: [
                { required: true, message: "Please repeat your password", trigger: "blur" },
                { validator: chkPwEqual, message: "Password must match", trigger: "blur" }
            ],
        };
        const editForm = reactive({
            id: "",
            username: "",
            password: "",
            password2: "",
            role: "",
            active: "",
        });
        let idx = -1;
        const handleEdit = (index, row) => {
            idx = index;
            Object.keys(editForm).forEach((item) => {
                if (item !== "password" && item !== "password2") {
                    editForm[item] = row[item];
                }
            });
            editVisible.value = true;
        };
        const saveEdit = () => {
            editVisible.value = false;
            ElMessage.success(`Successfully updated user ${editForm.username}.`);
            Object.keys(editForm).forEach((item) => {
                if (item !== "id" && item !== "password" && item !== "password2") {
                    res.tableData[idx][item] = editForm[item];
                }
            });
        };
        // const timeStampFormatter = (row, index) => {
        //     var d = new Date(row.login_time * 1000);
        //     // console.log(row.login_time);
        //     row.login_time = d.toLocaleString();
        //     return row.login_time;
        // };
        return {
            query,
            res,
            editVisible,
            editUser,
            editForm,
            chkPwEqual,
            editFormRules,
            handleSearch,
            handlePageChange,
            handleDelete,
            handleEdit,
            saveEdit,
            // timeStampFormatter,
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
