<template>
  <div class="player-list-container">
    
    <!-- 薪资范围筛选 -->
    <div class="salary-filter">
      <h4>薪资范围筛选</h4>
      <div class="filter-controls">
        <div class="filter-group">
          <label>下限：</label>
          <input 
            type="number" 
            v-model.number="salaryMin" 
            min="0" 
            max="6" 
            step="0.1"
            @change="fetchPlayers(currentPage)"
          >
          <span>千万美金</span>
        </div>
        <div class="filter-group">
          <label>上限：</label>
          <input 
            type="number" 
            v-model.number="salaryMax" 
            min="0" 
            max="6" 
            step="0.1"
            @change="fetchPlayers(currentPage)"
          >
          <span>千万美金</span>
        </div>
      </div>
    </div>
    
    <!-- 球员列表表格 -->
    <table class="player-table" v-if="players.length > 0">
      <thead>
        <tr>
          <th></th>
          <th>球员</th>
          <th>球队</th>
          <th>位置</th>
          <th>薪资</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in players" :key="player.id">
          <td class="player-avatar-cell">
            <img :src="`/player_avatars/${player.player_id}.png`" :alt="player.full_name" onerror="this.src='https://via.placeholder.com/60'">
          </td>
          <td class="player-name-cell">{{ player.full_name }}</td>
          <td class="player-team-cell">{{ translateTeam(player.team_name) }}</td>
          <td class="player-position-cell">{{ translatePosition(player.position) }}</td>
          <td class="player-salary-cell">${{ player.salary.toLocaleString() }}</td>
          <td class="player-action-cell">
            <button class="action-btn add-btn" @click="addPlayerToBench(player)">加入阵容</button>
          </td>
        </tr>
      </tbody>
    </table>
    
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
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import API_CONFIG from '../config/api'
import { translateTeam, translatePosition } from '../utils/translation'

// Props
const props = defineProps({
  excludePlayers: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['add-player'])

// 响应式数据
const players = ref([])
const loading = ref(false)
const error = ref('')
const pagination = ref(null)
const currentPage = ref(1)
const perPage = ref(15)
const salaryMin = ref(0)
const salaryMax = ref(6)

// API调用函数
const fetchPlayers = async (page = 1) => {
  loading.value = true
  error.value = ''
  
  try {
    const minSalaryUSD = salaryMin.value * 10000000 // 转换为美金
    const maxSalaryUSD = salaryMax.value * 10000000 // 转换为美金
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PLAYERS_INFORMATION}/list?page=${page}&per_page=${perPage.value}&salary_min=${minSalaryUSD}&salary_max=${maxSalaryUSD}`)
    
    if (!response.ok) {
      throw new Error('API调用失败')
    }
    
    const data = await response.json()
    // 过滤掉已经在阵容中的球员
    const filteredPlayers = data.players.filter(player => {
      return !props.excludePlayers.some(p => p.id === player.id)
    })
    players.value = filteredPlayers
    pagination.value = data.pagination
    currentPage.value = page
  } catch (err) {
    error.value = err.message
    players.value = []
    pagination.value = null
    currentPage.value = 1
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

// 将球员添加到替补阵容
const addPlayerToBench = (player) => {
  // 从球员列表中移除
  players.value = players.value.filter(p => p.id !== player.id)
  // 通知父组件添加球员
  emit('add-player', player)
}

// 监听excludePlayers变化，重新获取数据
watch(() => props.excludePlayers, () => {
  fetchPlayers(currentPage.value)
}, { deep: true })

// 页面挂载时获取数据
onMounted(() => {
  fetchPlayers()
})
</script>

<style scoped>
.player-list-container {
  flex: 1;
  min-width: 0;
}

h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

h4 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.salary-filter {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.filter-group input {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter-group span {
  font-size: 14px;
  color: #666;
}

.player-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.player-table th,
.player-table td {
  padding: 2px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.player-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.player-table tr:hover {
  background-color: #f5f5f5;
}

.player-avatar-cell {
  width: 60px;
}

.player-avatar-cell img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
}

.player-name-cell {
  font-weight: 500;
  color: #333;
  font-size: 15px;
}

.player-team-cell {
  color: #333;
  font-size: 15px;
}

.player-position-cell {
  color: #333;
  font-size: 15px;
}

.player-salary-cell {
  font-weight: 500;
  color: #4caf50;
  font-size: 15px;
}

.player-action-cell {
  width: 120px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  margin-right: 5px;
  margin-bottom: 5px;
}

.add-btn {
  background-color: #4caf50;
  color: white;
}

.add-btn:hover {
  background-color: #45a049;
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