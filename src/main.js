import Vue from 'vue'
import app from './App.vue'
import axios from 'axios'
import BootstrapVue from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueRouter from 'vue-router'

Vue.use(VueRouter)
Vue.use(BootstrapVue)

Vue.config.productionTip = false
import Home from "./components/Home"
import BookList from "./components/Books/BookList";
import BookDetail from "./components/Books/BookDetail";
import PageDetail from "./components/Pages/PageDetail";
import CharacterList from "./components/Characters/CharacterList"

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.withCredentials = true;

export const HTTP = axios.create({
  baseURL: "http://localhost"
})

const routes = [
  { path: "/", name: "HomeView", component: Home },
  { path: "/books", name: "BookListView", component: BookList },
  { path: "/books/:id", name: "BookDetailView", component: BookDetail },
  { path: "/pages/:id", name: "PageDetailView", component: PageDetail },
  { path: "/characters/", name: "CharacterListView", component: CharacterList },
]

const router = new VueRouter({
  mode: 'history',
  routes: routes
})

export const APIConstants = Object.freeze({ REST_PAGE_SIZE: 100 })

new Vue({
  router,
  render: h => h(app)
}).$mount('#app')
