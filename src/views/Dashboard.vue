<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="8">
                <el-card shadow="hover" class="mgb20" style="height:252px;">
                    <div class="user-info">
                        <img src="../assets/img/img.jpg" class="user-avator" alt />
                        <div class="user-info-cont">
                            <div class="user-info-name">{{ userData.username }}</div>
                            <div>{{ userData.role }}</div>
                        </div>
                    </div>
                    <div class="user-info-list">
                        Last Login Time:
                        <span>{{ userData.login_time }}</span>
                    </div>
                    <div class="user-info-list">
                        Last Login Location:
                        <span>--</span>
                    </div>
                </el-card>
                <el-card shadow="hover" style="height:252px;">
                    <template #header>
                        <div class="clearfix">
                            <span>T-Shirt Size</span>
                        </div>
                    </template>
                    Small
                    <el-progress :percentage="71.3" color="#42b983"></el-progress>
                    Medium
                    <el-progress :percentage="24.1" color="#f1e05a"></el-progress>
                    Large
                    <el-progress :percentage="13.7"></el-progress>
                    XLarge
                    <el-progress :percentage="5.9" color="#f56c6c"></el-progress>
                </el-card>
            </el-col>
            <el-col :span="16">
                <el-row :gutter="20" class="mgb20">
                    <el-col :span="8">
                        <el-card shadow="hover" :body-style="{ padding: '0px' }">
                            <div class="grid-content grid-con-1">
                                <i class="el-icon-user-solid grid-con-icon"></i>
                                <div class="grid-cont-right">
                                    <div class="grid-num">1234</div>
                                    <div>Users</div>
                                </div>
                            </div>
                        </el-card>
                    </el-col>
                    <el-col :span="8">
                        <el-card shadow="hover" :body-style="{ padding: '0px' }">
                            <div class="grid-content grid-con-2">
                                <i class="el-icon-s-marketing grid-con-icon"></i>
                                <div class="grid-cont-right">
                                    <div class="grid-num">321</div>
                                    <div>Projects</div>
                                </div>
                            </div>
                        </el-card>
                    </el-col>
                    <el-col :span="8">
                        <el-card shadow="hover" :body-style="{ padding: '0px' }">
                            <div class="grid-content grid-con-3">
                                <i class="el-icon-s-promotion grid-con-icon"></i>
                                <div class="grid-cont-right">
                                    <div class="grid-num">5000</div>
                                    <div>Versions</div>
                                </div>
                            </div>
                        </el-card>
                    </el-col>
                </el-row>
                <el-card shadow="hover" style="height:403px;">
                    <template #header>
                        <div class="clearfix">
                            <span>To-Do List</span>
                            <el-button style="float: right; padding: 3px 0" type="text">Add</el-button>
                        </div>
                    </template>

                    <el-table :show-header="false" :data="todoList" style="width:100%;">
                        <el-table-column width="40">
                            <template #default="scope">
                                <el-checkbox v-model="scope.row.status"></el-checkbox>
                            </template>
                        </el-table-column>
                        <el-table-column>
                            <template #default="scope">
                                <div class="todo-item" :class="{
                                        'todo-item-del': scope.row.status,
                                    }">{{ scope.row.title }}</div>
                            </template>
                        </el-table-column>
                        <el-table-column width="60">
                            <template>
                                <i class="el-icon-edit"></i>
                                <i class="el-icon-delete"></i>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </el-col>
        </el-row>
        <el-row :gutter="20">
            <el-col :span="12">
                <el-card shadow="hover">
                    <schart ref="bar" class="schart" canvasId="bar" :options="options"></schart>
                </el-card>
            </el-col>
            <el-col :span="12">
                <el-card shadow="hover">
                    <schart ref="line" class="schart" canvasId="line" :options="options2"></schart>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
import Schart from "vue-schart";
import { ref, reactive, getCurrentInstance } from "vue";
import { useStore } from "vuex";
export default {
    name: "dashboard",
    components: { Schart },
    setup() {
        const { proxy } = getCurrentInstance();
        const userData = reactive({});
        const store = useStore();
        // 获取表格数据
        const getData = () => {
            proxy.$api.get('/user/me').then(res => {
                userData.id = res.data.id;
                userData.username = res.data.username;
                userData.role = res.data.role;
                userData.login_time = new Date(res.data.login_time * 1000).toLocaleString()
            });
        };
        getData();

        const data = reactive([
            {
                name: "2018/09/04",
                value: 1083,
            },
            {
                name: "2018/09/05",
                value: 941,
            },
            {
                name: "2018/09/06",
                value: 1139,
            },
            {
                name: "2018/09/07",
                value: 816,
            },
            {
                name: "2018/09/08",
                value: 327,
            },
            {
                name: "2018/09/09",
                value: 228,
            },
            {
                name: "2018/09/10",
                value: 1065,
            },
        ]);
        const options = {
            type: "bar",
            title: {
                text: "Demo Weekly Dashboard",
            },
            xRorate: 25,
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
            datasets: [
                {
                    label: "RIM",
                    data: [234, 278, 270, 190, 230],
                },
                {
                    label: "CTMS",
                    data: [164, 178, 190, 135, 160],
                },
                {
                    label: "EDC",
                    data: [144, 198, 150, 235, 120],
                },
            ],
        };
        const options2 = {
            type: "line",
            title: {
                text: "Demo Monthly Dashboard",
            },
            labels: ["Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [
                {
                    label: "RIM",
                    data: [234, 278, 270, 190, 230],
                },
                {
                    label: "CTMS",
                    data: [164, 178, 150, 135, 160],
                },
                {
                    label: "EDC",
                    data: [74, 118, 200, 235, 90],
                },
            ],
        };
        const todoList = reactive([
            {
                title: "This is the 1st task.",
                status: false,
            },
            {
                title: "This is the 2nd task.",
                status: false,
            },
            {
                title: "This is the 3rd task.",
                status: false,
            },
            {
                title: "This is the 4th task.",
                status: false,
            },
            {
                title: "This is the 5th task.",
                status: true,
            },
            {
                title: "This is the 6th task.",
                status: true,
            },
        ]);

        return {
            userData,
            data,
            options,
            options2,
            todoList,
        };
    },
};
</script>

<style scoped>
.el-row {
    margin-bottom: 20px;
}

.grid-content {
    display: flex;
    align-items: center;
    height: 100px;
}

.grid-cont-right {
    flex: 1;
    text-align: center;
    font-size: 14px;
    color: #999;
}

.grid-num {
    font-size: 30px;
    font-weight: bold;
}

.grid-con-icon {
    font-size: 50px;
    width: 100px;
    height: 100px;
    text-align: center;
    line-height: 100px;
    color: #fff;
}

.grid-con-1 .grid-con-icon {
    background: rgb(45, 140, 240);
}

.grid-con-1 .grid-num {
    color: rgb(45, 140, 240);
}

.grid-con-2 .grid-con-icon {
    background: rgb(100, 213, 114);
}

.grid-con-2 .grid-num {
    color: rgb(45, 140, 240);
}

.grid-con-3 .grid-con-icon {
    background: rgb(242, 94, 67);
}

.grid-con-3 .grid-num {
    color: rgb(242, 94, 67);
}

.user-info {
    display: flex;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 2px solid #ccc;
    margin-bottom: 20px;
}

.user-avator {
    width: 120px;
    height: 120px;
    border-radius: 50%;
}

.user-info-cont {
    padding-left: 50px;
    flex: 1;
    font-size: 14px;
    color: #999;
}

.user-info-cont div:first-child {
    font-size: 30px;
    color: #222;
}

.user-info-list {
    font-size: 14px;
    color: #999;
    line-height: 25px;
}

.user-info-list span {
    margin-left: 70px;
}

.mgb20 {
    margin-bottom: 20px;
}

.todo-item {
    font-size: 14px;
}

.todo-item-del {
    text-decoration: line-through;
    color: #999;
}

.schart {
    width: 100%;
    height: 300px;
}
</style>
