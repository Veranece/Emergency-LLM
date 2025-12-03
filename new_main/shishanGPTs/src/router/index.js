import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import UserQAExamples from '../views/UserQAExamples.vue'
import RegulationsFiles from '../views/RegulationsFiles.vue'
// import SearchPage from '../views/SearchPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/examples',
    name: 'UserQAExamples',
    component: UserQAExamples
  },
  {
    path: '/regulations',
    name: 'RegulationsFiles',
    component: RegulationsFiles
  },
  // {
  //   path: '/search',
  //   name: 'Search',
  //   component: SearchPage
  // }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router 