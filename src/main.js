import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import api from './utils/request'
import installElementPlus from './plugins/element'
import './assets/css/icon.css'

const app = createApp(App)
installElementPlus(app)
app.config.globalProperties.$api = api
app
    .use(store)
    .use(router)
    .mount('#app')