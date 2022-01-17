import axios from 'axios';
import { ElMessageBox } from 'element-plus';
import { showLoading, hideLoading } from './loading';
import api_cfg from '../api_cfg';
import store from '../store';
import router from '../router';

// axios.defaults.headers.common['auth'] = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'

const api = axios.create({
    // process.env.NODE_ENV === 'development' 来判断是否开发环境
    baseURL: api_cfg.API_SERVER_URL,
    withCredentials: true,
    timeout: 10000,
});

// interceptors
api.interceptors.request.use(config => {
    showLoading();
    // 所有请求之前都要执行的操作
    // config.headers["access-control-allow-origin"] = 'http://127.0.0.1:8001/*';
    if ((config.url === '/auth/login' || config.url === '/auth/register') && config.method === 'post') {
        config.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8';
    } else if (config.method === 'get') {
        config.headers['Authorization'] = 'Bearer ' + localStorage.getItem("token");
    } else {
        config.headers['Authorization'] = 'Bearer ' + localStorage.getItem("token");
        config.headers['Content-Type'] = 'application/json; charset=utf-8';
    };
    // config.headers["Access-Control-Allow-Origin"] = "*";
    return config;
}, error => {
    // 错误处理
    hideLoading();
    return Promise.reject(error);
    // return Promise.reject(error.reponse.status);
});

// 响应拦截器
api.interceptors.response.use(function(response) {
    // 所有请求完成后都要执行的操作
    hideLoading();
    //API统一错误
    if (!response.data.status && response.status != 200) {
        alert('Error Msg: ' + response.data.message);
        return Promise.reject(response.data.message);
    }
	return response;
}, function(error) {
    // 错误处理
    hideLoading();
    //doesn't matter which error, move to login page'
    // console.log(error);
    alert(error);
    localStorage.removeItem("ms_username");
    localStorage.removeItem("token");
    store.commit("logOutUser");
    router.push('/login');
    // if (error.response.status == 403) {
    //     alert(error.response.data.message);
    //     store.commit('delToken');
    //     router.push('/auth/login');
    // }

    return Promise.reject(error);
});

// //encapsulate requests
// api.get = function(url, params) {
//     return new Promise((resolve, reject) => {
//         // console.log(localStorage.getItem('token'));
//         axios({
//             method: 'get',
//             url: api_cfg.API_SERVER_URL + url,
//             params: params,
//             headers: {
//                 'Authorization': 'Bearer ' + store.state.userInfo.token,
//             }
//         }).then(response => {
//             switch (response.status) {
//                 case 200:
//                     resolve(response);
//                     break;
//                 default:
//                     reject(response)
//             }
//         })
//     })
// };


// //encapsulate requests
// api.options = function(url, params) {
//     return new Promise((resolve, reject) => {
//         // console.log(localStorage.getItem('token'));
//         axios({
//             method: 'options',
//             url: api_cfg.API_SERVER_URL + url,
//             params: params,
//             headers: {
//                 'Authorization': 'Bearer ' + store.state.userInfo.token,
//             }
//         }).then(response => {
//             switch (response.status) {
//                 case 200:
//                     resolve(response);
//                     break;
//                 default:
//                     reject(response)
//             }
//         })
//     })
// };

// api.post = function(url, data) {
//     return new Promise((resolve, reject) => {
//         let cType = 'application/json; charset=utf-8';
//         if (url === "/auth/login") cType = 'application/x-www-form-urlencoded';
//         axios({
//             method: 'post',
//             url: api_cfg.API_SERVER_URL + url,
//             data: data,
//             headers: {
//                 'Content-Type': cType,
//                 'Authorization': 'Bearer ' + store.state.userInfo.token,
//             }
//         }).then(response => {
//             switch (response.status) {
//                 case 200:
//                     resolve(response);
//                     break;
//                 default:
//                     reject(response)
//             }
//         })
//     })
// };

// api.put = function(url, data) {
//     return new Promise((resolve, reject) => {
//         axios({
//             method: 'put',
//             url: api_cfg.API_SERVER_URL + url,
//             data: data,
//             headers: {
//                 'Content-Type': 'application/json; charset=utf-8',
//                 'Authorization': 'Bearer ' + store.state.userInfo.token,
//             },
//         }).then(response => {
//             switch (response.status) {
//                 case 200:
//                     resolve(response);
//                     break;
//                 default:
//                     reject(response)
//             }
//         })
//     })
// };

export default api;
