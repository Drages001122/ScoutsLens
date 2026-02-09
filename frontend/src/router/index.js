import { createRouter, createWebHistory } from 'vue-router'
import TeamSelection from '../views/TeamSelection.vue'
import Rankings from '../views/Rankings.vue'
import Login from '../views/Login.vue'
import LineupRatings from '../views/LineupRatings.vue'
import PlayerComparison from '../views/PlayerComparison.vue'
import ValueForMoney from '../views/ValueForMoney.vue'

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
  },
  {
    path: '/player-comparison',
    name: 'PlayerComparison',
    component: PlayerComparison
  },
  {
    path: '/value-for-money',
    name: 'ValueForMoney',
    component: ValueForMoney
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，确保访问其他页面前必须登录
router.beforeEach(async (to, from, next) => {
  // 不需要登录的页面
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)
  
  // 检查用户是否已登录
  const token = localStorage.getItem('token')
  
  if (authRequired && !token) {
    // 未登录，重定向到登录页面
    next('/login')
    return
  }
  
  if (authRequired && token) {
    // 已登录，验证令牌有效性
    try {
      const response = await fetch('/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        // 令牌无效，清除令牌并重定向到登录页面
        localStorage.removeItem('token')
        next('/login')
        return
      }
      
      // 令牌有效，允许访问
      next()
    } catch (error) {
      // 验证过程中出错，清除令牌并重定向到登录页面
      localStorage.removeItem('token')
      next('/login')
    }
  } else {
    // 访问的是公开页面，允许访问
    next()
  }
})

export default router