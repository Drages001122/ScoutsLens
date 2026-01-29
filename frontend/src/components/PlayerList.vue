<template>
  <div class="player-list-container">
    
    <!-- 筛选器容器 -->
    <div class="filters-container">
      <!-- 薪资范围筛选 -->
      <div class="filter-section salary-filter">
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
      
      <!-- 球队筛选 -->
      <div class="filter-section team-filter">
        <h4>球队筛选</h4>
        <div class="filter-controls">
          <button 
            class="team-filter-btn" 
            @click="showTeamModal = true"
          >
            选择球队 (已选 {{ selectedTeams.length }} 支)
          </button>
        </div>
      </div>
    </div>
    
    <!-- 球队选择弹窗 -->
    <div class="modal-overlay" v-if="showTeamModal" @click="closeTeamModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>选择球队</h3>
          <button class="close-btn" @click="closeTeamModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="team-logo-grid">
            <div 
              v-for="(teamCN, teamEN) in teams" 
              :key="teamEN"
              class="team-logo-item"
              :class="{ selected: selectedTeams.includes(teamEN) }"
              @click="toggleTeam(teamEN)"
            >
              <img 
                :src="`/team_logos/${teamLogoMap[teamEN]}`" 
                :alt="teamEN"
                class="team-logo"
                onerror="this.src='https://via.placeholder.com/60'"
              >
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn clear-btn" @click="clearTeams">清空</button>
          <button class="modal-btn select-all-btn" @click="selectAllTeams">全选</button>
          <button class="modal-btn confirm-btn" @click="confirmTeamSelection">确认</button>
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
            <img 
              :src="`/player_avatars/${player.player_id}.png`" 
              :alt="player.full_name" 
              onerror="this.src='https://via.placeholder.com/60'"
              class="player-avatar"
              @click="openPlayerProfile(player)"
            >
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
      <div class="per-page-selector">
        <label>每页数量：</label>
        <select v-model="perPage" @change="handlePerPageChange">
          <option value="10">10</option>
          <option value="15">15</option>
          <option value="20">20</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
      </div>
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
    
    <!-- 球员个人介绍弹窗 -->
    <PlayerProfile 
      :visible="showPlayerProfile"
      :player="selectedPlayer"
      @close="closePlayerProfile"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import API_CONFIG from '../config/api'
import { translateTeam, translatePosition } from '../utils/translation'
import translations from '../data/translations.json'
import PlayerProfile from './PlayerProfile.vue'

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
const selectedTeams = ref([])
const teams = ref(translations.teams)
const showTeamModal = ref(false)
// 球员个人介绍相关状态
const showPlayerProfile = ref(false)
const selectedPlayer = ref(null)

// 球队名称到图片文件名的映射
const teamLogoMap = {
  '76ers': 'PHI_logo.png',
  'Bucks': 'MIL_logo.png',
  'Bulls': 'CHI_logo.png',
  'Cavaliers': 'CLE_logo.png',
  'Celtics': 'BOS_logo.png',
  'Clippers': 'LAC_logo.png',
  'Grizzlies': 'MEM_logo.png',
  'Hawks': 'ATL_logo.png',
  'Heat': 'MIA_logo.png',
  'Hornets': 'CHA_logo.png',
  'Jazz': 'UTA_logo.png',
  'Kings': 'SAC_logo.png',
  'Knicks': 'NYK_logo.png',
  'Lakers': 'LAL_logo.png',
  'Magic': 'ORL_logo.png',
  'Mavericks': 'DAL_logo.png',
  'Nets': 'BKN_logo.png',
  'Nuggets': 'DEN_logo.png',
  'Pacers': 'IND_logo.png',
  'Pelicans': 'NOP_logo.png',
  'Pistons': 'DET_logo.png',
  'Raptors': 'TOR_logo.png',
  'Rockets': 'HOU_logo.png',
  'Spurs': 'SAS_logo.png',
  'Suns': 'PHX_logo.png',
  'Thunder': 'OKC_logo.png',
  'Timberwolves': 'MIN_logo.png',
  'Trail Blazers': 'POR_logo.png',
  'Warriors': 'GSW_logo.png',
  'Wizards': 'WAS_logo.png'
}

// API调用函数
const fetchPlayers = async (page = 1) => {
  loading.value = true
  error.value = ''
  
  try {
    const minSalaryUSD = salaryMin.value * 10000000 // 转换为美金
    const maxSalaryUSD = salaryMax.value * 10000000 // 转换为美金
    
    // 构建查询参数
    let queryParams = new URLSearchParams()
    queryParams.append('page', page)
    queryParams.append('per_page', perPage.value)
    queryParams.append('salary_min', minSalaryUSD)
    queryParams.append('salary_max', maxSalaryUSD)
    
    // 添加球队筛选参数
    selectedTeams.value.forEach(team => {
      queryParams.append('teams', team)
    })
    
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PLAYERS_INFORMATION}/list?${queryParams.toString()}`)
    
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

// 处理每页数量变化
const handlePerPageChange = () => {
  // 当每页数量变化时，重置到第一页
  currentPage.value = 1
  fetchPlayers(1)
}

// 将球员添加到替补阵容
const addPlayerToBench = (player) => {
  // 从球员列表中移除
  players.value = players.value.filter(p => p.id !== player.id)
  // 通知父组件添加球员
  emit('add-player', player)
}

// 关闭球队选择弹窗
const closeTeamModal = () => {
  showTeamModal.value = false
}

// 切换球队选中状态
const toggleTeam = (teamEN) => {
  const index = selectedTeams.value.indexOf(teamEN)
  if (index > -1) {
    selectedTeams.value.splice(index, 1)
  } else {
    selectedTeams.value.push(teamEN)
  }
}

// 清空所有选中球队
const clearTeams = () => {
  selectedTeams.value = []
}

// 全选所有球队
const selectAllTeams = () => {
  selectedTeams.value = Object.keys(teams.value)
}

// 确认球队选择并关闭弹窗
const confirmTeamSelection = () => {
  fetchPlayers(currentPage.value)
  closeTeamModal()
}

// 打开球员个人介绍弹窗
const openPlayerProfile = (player) => {
  selectedPlayer.value = player
  showPlayerProfile.value = true
}

// 关闭球员个人介绍弹窗
const closePlayerProfile = () => {
  showPlayerProfile.value = false
  selectedPlayer.value = null
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

.filters-container {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.filter-section {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.salary-filter {
  flex: 2;
  min-width: 0;
}

.team-filter {
  flex: 1;
  min-width: 0;
}

.team-selector {
  width: 100%;
}

.team-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  cursor: pointer;
  min-height: 120px;
}

.team-select-info {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  text-align: center;
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
  padding: 12px;
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

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.player-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
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
  gap: 15px;
  margin-top: 20px;
}

.per-page-selector {
  display: flex;
  align-items: center;
  gap: 5px;
}

.per-page-selector label {
  font-size: 14px;
  color: #666;
}

.per-page-selector select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  cursor: pointer;
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

/* 球队筛选按钮样式 */
.team-filter-btn {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.3s ease;
}

.team-filter-btn:hover {
  background-color: #f5f5f5;
  border-color: #4caf50;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.modal-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.clear-btn {
  background-color: #fff;
  color: #333;
}

.clear-btn:hover {
  background-color: #f5f5f5;
  border-color: #ff5252;
  color: #ff5252;
}

.select-all-btn {
  background-color: #fff;
  color: #333;
}

.select-all-btn:hover {
  background-color: #f5f5f5;
  border-color: #4caf50;
  color: #4caf50;
}

.confirm-btn {
  background-color: #4caf50;
  color: #fff;
  border-color: #4caf50;
}

.confirm-btn:hover {
  background-color: #45a049;
  border-color: #45a049;
}

/* 球队LOGO网格样式 */
.team-logo-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.team-logo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 7px;
  border: 4px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  width: 100px;
  height: 100px;
}

.team-logo-item:hover {
  border-color: #4caf50;
  background-color: #f0f8f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.team-logo-item.selected {
  border-color: #4caf50;
  background-color: #e8f5e8;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.team-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: #fff;
  border-radius: 6px;
  padding: 8px;
}



/* 响应式调整 */
@media (max-width: 1200px) {
  .team-logo-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .team-logo-item {
    width: 90px;
    height: 90px;
  }
}

@media (max-width: 900px) {
  .team-logo-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .team-logo-item {
    width: 80px;
    height: 80px;
  }
}

@media (max-width: 768px) {
  .filters-container {
    flex-direction: column;
  }
  
  .team-logo-grid {
    grid-template-columns: repeat(5, 1fr);
  }
  
  .modal-content {
    width: 98%;
    max-width: 95vw;
  }
  
  .team-logo-item {
    width: 70px;
    height: 70px;
  }
}

@media (max-width: 480px) {
  .team-logo-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  
  .team-logo-item {
    width: 60px;
    height: 60px;
  }
  
  .team-logo {
    padding: 4px;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-group input {
    width: 100px;
  }
}
</style>
