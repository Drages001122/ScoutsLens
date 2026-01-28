import { createRouter, createWebHistory } from 'vue-router'
import TeamSelection from '../views/TeamSelection.vue'
import Rankings from '../views/Rankings.vue'

const routes = [
  {
    path: '/',
    redirect: '/team-selection'
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router