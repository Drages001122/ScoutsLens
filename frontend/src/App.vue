<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const user = ref(null)
const showDropdown = ref(false)

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    user.value = JSON.parse(userStr)
  } else {
    user.value = null
  }
}

onMounted(() => {
  loadUser()
})

watch(route, () => {
  loadUser()
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  user.value = null
  router.push('/login')
}
</script>

<template>
  <div class="app">
    <header class="banner">
      <div class="banner-left">
        <router-link to="/team-selection" class="banner-item">阵容选择</router-link>
        <router-link to="/rankings" class="banner-item">排行榜</router-link>
        <router-link to="/lineup-ratings" class="banner-item">阵容评分</router-link>
        <router-link to="/player-comparison" class="banner-item">球员比较</router-link>
        <router-link to="/value-for-money" class="banner-item">性价比</router-link>
      </div>
      <div class="banner-right">
        <div v-if="user" class="user-info">
          <div class="username-dropdown" @click="showDropdown = !showDropdown">
            <span class="username">{{ user.username }}</span>
            <span class="dropdown-arrow"></span>
          </div>
          <div v-if="showDropdown" class="dropdown-menu">
            <button @click="handleLogout" class="logout-button">退出登录</button>
          </div>
        </div>
        <router-link v-else to="/login" class="login-link">登录</router-link>
      </div>
    </header>

    <main class="content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.app {
  font-family: Arial, sans-serif;
}

.banner {
  background-color: rgb(13, 43, 90);
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  box-sizing: border-box;
}

.banner-left {
  display: flex;
  align-items: center;
}

.banner-right {
  display: flex;
  align-items: center;
}

.banner-item {
  color: white;
  text-decoration: none;
  margin: 0 10px;
  font-size: 18px;
  font-weight: bold;
  padding: 10px 15px;
  border-radius: 5px;
  transition: color 0.3s;
}

.banner-item:hover {
  color: #ffcc00;
}

.user-info {
  display: flex;
  align-items: center;
  position: relative;
}

.username-dropdown {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: color 0.3s;
}

.username-dropdown:hover .username {
  color: #ffcc00;
}

.username {
  color: white;
  font-size: 16px;
  font-weight: bold;
}

.dropdown-arrow {
  color: white;
  font-size: 12px;
  transition: transform 0.3s;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 5px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  min-width: 120px;
  z-index: 1001;
}

.logout-button {
  background-color: transparent;
  color: #333;
  border: none;
  padding: 10px 15px;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #f0f0f0;
}

.login-link {
  color: white;
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
  padding: 8px 16px;
  border: 2px solid white;
  border-radius: 4px;
  transition: all 0.3s;
}

.login-link:hover {
  background-color: white;
  color: rgb(13, 43, 90);
}

.content {
  padding: 20px;
  padding-top: 80px;
}
</style>
