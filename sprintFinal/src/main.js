import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingPage from './views/LandingPage.vue'
import Dashboard from './views/Dashboard.vue'
import { preloadData } from './utils/dataCache'
import './assets/main.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Landing',
      component: LandingPage
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: Dashboard
    }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')

// Preload data in background for better performance
preloadData()