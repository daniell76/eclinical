<template>
    <div v-bind:class="bgCss">
        <div class="ms-login">
            <div class="ms-title">Calyx Application Cost Estimation</div>
            <el-form v-if="pageTag.tag === 'REGISTER'" :model="reg_param" :rules="reg_rules" ref="reg" label-width="0px" class="ms-content">
                <el-form-item prop="username">
                    <el-input v-model="reg_param.username" placeholder="username">
                        <template #prepend>
                            <el-button icon="el-icon-user"></el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input type="password" placeholder="password" v-model="reg_param.password"
                        @keyup.enter="submitRegForm()">
                        <template #prepend>
                            <el-button icon="el-icon-lock"></el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="password2">
                    <el-input type="password" placeholder="repeat password" v-model="reg_param.password2"
                        @keyup.enter="submitRegForm()">
                        <template #prepend>
                            <el-button icon="el-icon-lock"></el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <div class="login-btn">
                    <el-button type="primary" @click="submitRegForm()">register</el-button>
                </div>
                <div class="login-btn">
                    <el-button type="primary" @click="changePageTag('LOGIN')">=> Goto login page ...</el-button>
                </div>
                <!-- <p class="login-tips">Tips: Input any username or password。</p> -->
            </el-form>
            <el-form v-else :model="param" :rules="rules" ref="login" label-width="0px" class="ms-content">
                <el-form-item prop="username">
                    <el-input v-model="param.username" placeholder="username">
                        <template #prepend>
                            <el-button icon="el-icon-user"></el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input type="password" placeholder="password" v-model="param.password"
                        @keyup.enter="submitForm()">
                        <template #prepend>
                            <el-button icon="el-icon-lock"></el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <div class="login-btn">
                    <el-button type="primary" @click="submitForm()">login</el-button>
                </div>
                <div class="login-btn">
                    <el-button type="primary" @click="changePageTag('REGISTER')">=> To register a new user ...</el-button>
                </div>
                <!-- <p class="login-tips">Tips: Input any username or password。</p> -->
            </el-form>
        </div>
    </div>
</template>

<script>
import { ref, reactive, onMounted, onUpdated, onUnmounted, getCurrentInstance } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import qs from "qs"

export default {
    setup() {
        const { proxy } = getCurrentInstance();
        const router = useRouter();
        const pageTag = reactive({
            tag: "LOGIN"
        });
        // Login parameters
        const param = reactive({
            username: "test",
            password: "test",
        });

        const rules = {
            username: [
                { required: true, message: "Please input username", trigger: "blur" },
                { min: 3, message: "at least 3 charecters", trigger: "blur" }
            ],
            password: [
                { required: true, message: "Please input password", trigger: "blur" },
                { min: 3, message: "at least 3 charecters", trigger: "blur" }
            ],
        };
        const login = ref(null);
        const submitForm = () => {
            login.value.validate((valid) => {
                if (valid) {
                    console.log(valid);
                    proxy.$api.post('/auth/login', qs.stringify(param))
                    .then(res => {
                        const userInfo = {
                            username: res.data.data.username,
                            role: res.data.data.role,
                            token: res.data.data.access_token
                        };
                        store.commit("logInUser", userInfo);
                        localStorage.setItem("ms_username", userInfo.username);
                        localStorage.setItem("token", userInfo.token);
                        // proxy.$api.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem("token");
                    })
                    .then(res => {
                        ElMessage.success("Login Successful");
                        router.push("/");
                    });
                } else {
                    ElMessage.error("Login Failed");
                    return false;
                }
                console.log(login);
            });
        };

        // Register parameters
        const reg_param = reactive({
            username: "",
            password: "",
            password2: "",
        });
        const chkPwEqual = (rule, value, callback) => {
            if (reg_param.password === value) {
                callback()
            } else {
                callback(new Error("Password does not match!"))
            }
        };
        const reg_rules = {
            username: [
                { required: true, message: "Please pick your username", trigger: "blur" },
                { min: 3, message: "at least 3 charecters", trigger: "blur" }
            ],
            password: [
                { required: true, message: "Please set your password", trigger: "blur" },
                { min: 3, message: "at least 3 charecters", trigger: "blur" }
            ],
            password2: [
                { required: true, message: "Please repeat your password", trigger: "blur" },
                { validator: chkPwEqual, message: "Password must match", trigger: "blur" }
            ],
        };
        const reg = ref(null);
        const submitRegForm = () => {
            reg.value.validate((valid) => {
                if (valid) {
                    let reg_api_param = {
                        username: reg_param.username,
                        password: reg_param.password
                    };
                    proxy.$api.post('/auth/register', qs.stringify(reg_api_param))
                    .then(res => {
                        ElMessage.success("Registration Successful");
                        pageTag.tag = "LOGIN";  // switch to login page
                    });
                } else {
                    ElMessage.error("Please fix the error and retry.");
                    return false;
                }
            });
        };
        const changePageTag = (tag) => {
            pageTag.tag = tag;
        };
        
        const store = useStore();
        store.commit("clearTags");
        
        var bgImgIdx = Math.floor(Math.random() * 10) + 1;
        // bgImg = "../assets/img/calyx-1/calyx-1-" + bgImgIdx.toString().padStart(2, "0") + ".jpg"
        // style_login_wrap = "position: relative; width: 100%; height: 100%; background-image: url(" + bgImg + "); background-size: 100%;"
        var bgCss = "login-wrap login-wrap-bg-" + bgImgIdx.toString();
        
        return {
            pageTag,
            param,
            reg_param,
            rules,
            reg_rules,
            login,
            reg,
            bgCss,
            submitForm,
            submitRegForm,
            chkPwEqual,
            changePageTag,
        };
    },
};
</script>

<!-- <style scoped> -->
<style>
.ms-title {
    width: 100%;
    line-height: 50px;
    text-align: center;
    font-size: 20px;
    color: #fff;
    border-bottom: 1px solid #ddd;
}
.ms-login {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 350px;
    margin: -190px 0 0 -175px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.3);
    overflow: hidden;
}
.ms-content {
    padding: 30px 30px;
}
.login-btn {
    text-align: center;
}
.login-btn button {
    width: 100%;
    height: 36px;
    margin-bottom: 10px;
   border-color: #410099;
   background-color: #410099;
}
.login-btn button:hover {
    border-color: #7a54ff;
    background-color: #7a54ff;
}
.login-tips {
    font-size: 12px;
    line-height: 30px;
    color: #fff;
}
.login-wrap {
    position: relative;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-repeat: no-repeat;
}
.login-wrap-bg-1 {
    background-image: url(../assets/img/calyx/calyx-01.jpg);
}
.login-wrap-bg-2 {
    background-image: url(../assets/img/calyx/calyx-02.jpg);
}
.login-wrap-bg-3 {
    background-image: url(../assets/img/calyx/calyx-03.jpg);
}
.login-wrap-bg-4 {
    background-image: url(../assets/img/calyx/calyx-04.jpg);
}
.login-wrap-bg-5 {
    background-image: url(../assets/img/calyx/calyx-05.jpg);
}
.login-wrap-bg-6 {
    background-image: url(../assets/img/calyx/calyx-06.jpg);
}
.login-wrap-bg-7 {
    background-image: url(../assets/img/calyx/calyx-07.jpg);
}
.login-wrap-bg-8 {
    background-image: url(../assets/img/calyx/calyx-08.jpg);
}
.login-wrap-bg-9 {
    background-image: url(../assets/img/calyx/calyx-09.jpg);
}
.login-wrap-bg-10 {
    background-image: url(../assets/img/calyx/calyx-10.jpg);
}
</style>