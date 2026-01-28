<template>
  <div class="page">
    <h2>阵容选择页面</h2>
    
    <div class="player-list-container">
      <h3>NBA球员列表</h3>
      
      <!-- 球员列表 -->
      <div class="player-list" v-if="players.length > 0">
        <div class="player-item" v-for="player in players" :key="player.id">
          <div class="player-avatar">
            <img :src="`${API_CONFIG.BASE_URL}/api/player_avatar/${player.player_id}`" :alt="player.full_name" onerror="this.src='https://via.placeholder.com/60'">
          </div>
          <div class="player-info">
            <div class="player-name">{{ player.full_name }}</div>
            <div class="player-details">
              <span class="team">{{ player.team_name }}</span>
              <span class="position">{{ player.position }}</span>
              <span class="salary">${{ player.salary.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading" v-else-if="loading">
        加载中...
      </div>
      
      <!-- 错误状态 -->
      <div class="error" v-else-if="error">
        {{ error }}
      </div>
      
      <!-- 无数据状态 -->
      <div class="no-data" v-else>
        暂无球员数据
      </div>
      
      <!-- 分页控件 -->
      <div class="pagination" v-if="pagination">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="changePage(1)"
        >
          首页
        </button>
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ pagination.total_pages }} 页
        </span>
        
        <button 
          class="page-btn" 
          :disabled="currentPage === pagination.total_pages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
        <button 
          class="page-btn" 
          :disabled="currentPage === pagination.total_pages"
          @click="changePage(pagination.total_pages)"
        >
          末页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import API_CONFIG from '../config/api'

// 响应式数据
const players = ref([])
const loading = ref(false)
const error = ref('')
const pagination = ref(null)
const currentPage = ref(1)
const perPage = ref(10)

// API调用函数
const fetchPlayers = async (page = 1) => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PLAYERS}?page=${page}&per_page=${perPage.value}`)
    
    if (!response.ok) {
      throw new Error('API调用失败')
    }
    
    const data = await response.json()
    players.value = data.players
    pagination.value = data.pagination
    currentPage.value = page
  } catch (err) {
    error.value = err.message
    players.value = []
    pagination.value = null
  } finally {
    loading.value = false
  }
}

// 分页函数
const changePage = (page) => {
  if (page >= 1 && (!pagination.value || page <= pagination.value.total_pages)) {
    fetchPlayers(page)
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchPlayers()
})
</script>

<style scoped>
.page {
  padding: 20px;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

.player-list-container {
  max-width: 1200px;
  margin: 0 auto;
}

.player-list {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.player-item {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.player-item:last-child {
  border-bottom: none;
}

.player-item:hover {
  background-color: #f5f5f5;
}

.player-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #f0f0f0;
}

.player-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.player-info {
  flex: 1;
}

.player-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
  color: #333;
}

.player-details {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.team {
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.position {
  background-color: #e3f2fd;
  padding: 2px 8px;
  border-radius: 4px;
  color: #1976d2;
}

.salary {
  font-weight: 500;
  color: #4caf50;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background-color: #f0f0f0;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #666;
}

.error {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #f44336;
}

.no-data {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #666;
}
</style>