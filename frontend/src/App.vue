<script setup>
// App.vue
</script>

<template>
  <div class="app">
    <!-- Banner 位 -->
    <header class="banner">
      <router-link to="/team-selection" class="banner-item">阵容选择</router-link>
      <router-link to="/rankings" class="banner-item">排行榜</router-link>
    </header>
    
    <!-- 页面内容 -->
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
  padding: 15px 0;
  text-align: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}

.banner-item {
  color: white;
  text-decoration: none;
  margin: 0 20px;
  font-size: 18px;
  font-weight: bold;
  padding: 10px 15px;
  border-radius: 5px;
  transition: color 0.3s;
}

.banner-item:hover {
  color: #ffcc00;
}

.content {
  padding: 20px;
  padding-top: 80px;
}
</style>
