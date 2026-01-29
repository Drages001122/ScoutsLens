import { createRouter, createWebHistory } from 'vue-router'
import TeamSelection from '../views/TeamSelection.vue'
import Rankings from '../views/Rankings.vue'
import Login from '../views/Login.vue'
import LineupRatings from '../views/LineupRatings.vue'

const routes = [
  {
    path: '/',
    redirect: '/team-selection'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/team-selection',
    name: 'TeamSelection',
    component: TeamSelection
  },
  {
    path: '/rankings',
    name: 'Rankings',
    component: Rankings
  },
  {
    path: '/lineup-ratings',
    name: 'LineupRatings',
    component: LineupRatings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，确保访问其他页面前必须登录
router.beforeEach((to, from, next) => {
  // 不需要登录的页面
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)
  
  // 检查用户是否已登录
  const loggedIn = localStorage.getItem('token')
  
  if (authRequired && !loggedIn) {
    // 未登录，重定向到登录页面
    next('/login')
  } else {
    // 已登录或访问的是公开页面，允许访问
    next()
  }
})

export default router