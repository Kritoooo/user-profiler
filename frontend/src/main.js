import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './views/Home.vue'
import Timeline from './views/Timeline.vue'
import Profile from './views/Profile.vue'
import Logs from './views/Logs.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/timeline/:userId', component: Timeline, props: true },
  { path: '/profile/:userId', component: Profile, props: true },
  { path: '/logs', component: Logs }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')