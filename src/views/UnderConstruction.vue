<template>
    <div class="error-page">
        <div class="error-code">CTMS</div>
        <div class="error-desc">Under Construction</div>
        <div class="error-handle">
            <router-link to="/">
                <el-button type="primary" size="large">Home</el-button>
            </router-link>
            <el-button class="error-btn" type="primary" size="large" @click="goBack">Go Back</el-button>
        </div>
    </div>
</template>

<script>
import { useRouter } from "vue-router";
export default {
    name: "Under Construction",
    setup() {
        const router = useRouter();
        const goBack = () => {
            router.go(-1);
        };
        return {
            goBack,
        };
    },
};
</script>


<style scoped>
.error-page {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background: #f3f3f3;
    box-sizing: border-box;
}
.error-code {
    line-height: 1;
    font-size: 250px;
    font-weight: bolder;
    color: #2d8cf0;
}
.error-code span {
    color: #00a854;
}
.error-desc {
    font-size: 30px;
    color: #777;
}
.error-handle {
    margin-top: 30px;
    padding-bottom: 200px;
}
.error-btn {
    margin-left: 100px;
}
</style>
