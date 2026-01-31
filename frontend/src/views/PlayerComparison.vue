<template>
  <div class="player-comparison-container">
    <h1>球员比较</h1>
    
    <!-- 球队和球员选择区域 -->
    <div class="player-selection-section">
      <div class="selection-controls">
        <!-- 球队选择 -->
        <div class="team-selector">
          <label for="team-select">选择球队：</label>
          <select 
            id="team-select" 
            v-model="selectedTeam"
            @change="handleTeamChange"
            :disabled="isLoadingTeams"
          >
            <option value="">请选择球队</option>
            <option 
              v-for="team in teams" 
              :key="team.team_id"
              :value="team.team_id"
            >
              {{ translateTeam(team.team_name) }}
            </option>
          </select>
        </div>
        
        <!-- 球员选择 -->
        <div class="player-selector" v-if="selectedTeam">
          <label for="player-select">选择球员：</label>
          <select 
            id="player-select" 
            v-model="selectedPlayerId"
            :disabled="isLoadingPlayers"
          >
            <option value="">请选择球员</option>
            <option 
              v-for="player in players" 
              :key="player.player_id"
              :value="player.player_id"
            >
              {{ player.full_name }}
            </option>
          </select>
          <button 
            class="add-player-btn"
            @click="addPlayer"
            :disabled="!selectedPlayerId || isLoading"
          >
            添加球员
          </button>
        </div>
      </div>
      
      <!-- 已添加的球员列表 -->
      <div class="selected-players" v-if="comparisonPlayers.length > 0">
        <h3>已添加的球员：</h3>
        <div class="players-list">
          <div 
            v-for="player in comparisonPlayers" 
            :key="player.player_id"
            class="player-item"
          >
            <img 
              :src="`/player_avatars/${player.player_id}.png`" 
              :alt="player.full_name"
              class="player-avatar-small"
              onerror="this.src='https://via.placeholder.com/40'"
            >
            <span class="player-name">{{ player.full_name }}</span>
            <span class="player-team">{{ translateTeam(player.team_name) }}</span>
            <button 
              class="remove-player-btn"
              @click="removePlayer(player.player_id)"
              :disabled="isLoading"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图表区域 -->
    <div class="chart-section" v-if="comparisonPlayers.length > 0">
      <h3>球员表现比较</h3>
      <div class="chart-container">
        <canvas ref="comparisonChart"></canvas>
      </div>
    </div>
    
    <!-- 空状态提示 -->
    <div class="empty-state" v-if="comparisonPlayers.length === 0">
      <p>请添加球员以进行比较</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { translateTeam } from '../utils/translation'

// 响应式数据
const teams = ref([])
const players = ref([])
const selectedTeam = ref('')
const selectedPlayerId = ref('')
const comparisonPlayers = ref([])
const comparisonData = ref({})
const isLoadingTeams = ref(false)
const isLoadingPlayers = ref(false)
const isLoading = ref(false)

// 图表相关
const comparisonChart = ref(null)
const chartInstance = ref(null)

// 加载所有球队
const loadTeams = async () => {
  try {
    isLoadingTeams.value = true
    console.log('开始加载球队列表...')
    const response = await fetch('/api/basic_information/teams')
    console.log('球队列表请求响应状态:', response.status)
    console.log('球队列表请求响应URL:', response.url)
    if (!response.ok) {
      const errorText = await response.text()
      console.error('获取球队列表失败:', errorText)
      throw new Error(`获取球队列表失败: ${response.status} ${errorText}`)
    }
    const data = await response.json()
    console.log('球队列表数据:', data)
    teams.value = data.teams || []
    console.log('加载的球队数量:', teams.value.length)
  } catch (error) {
    console.error('加载球队失败:', error)
    // 添加模拟数据作为备份
    teams.value = [
      { team_id: 1, team_name: 'LAL' },
      { team_id: 2, team_name: 'BOS' },
      { team_id: 3, team_name: 'NYK' },
      { team_id: 4, team_name: 'GSW' },
      { team_id: 5, team_name: 'LAC' }
    ]
    console.log('使用模拟球队数据:', teams.value)
  } finally {
    isLoadingTeams.value = false
  }
}

// 加载球队的球员
const loadPlayers = async (teamId) => {
  if (!teamId) {
    players.value = []
    return
  }
  
  try {
    isLoadingPlayers.value = true
    console.log('开始加载球队球员列表，teamId:', teamId)
    const response = await fetch(`/api/basic_information/team/${teamId}/players`)
    console.log('球员列表请求响应状态:', response.status)
    if (!response.ok) {
      const errorText = await response.text()
      console.error('获取球员列表失败:', errorText)
      throw new Error(`获取球员列表失败: ${response.status} ${errorText}`)
    }
    const data = await response.json()
    console.log('球员列表数据:', data)
    players.value = data.players || []
    console.log('加载的球员数量:', players.value.length)
  } catch (error) {
    console.error('加载球员失败:', error)
    // 添加模拟数据作为备份
    const teamNames = ['LAL', 'BOS', 'NYK', 'GSW', 'LAC']
    const teamName = teamNames[parseInt(teamId) - 1] || 'Team'
    players.value = [
      {
        player_id: parseInt(teamId) * 100 + 1,
        full_name: `${teamName} Player 1`,
        team_name: teamName,
        position: 'PG',
        salary: 30000000
      },
      {
        player_id: parseInt(teamId) * 100 + 2,
        full_name: `${teamName} Player 2`,
        team_name: teamName,
        position: 'SG',
        salary: 25000000
      },
      {
        player_id: parseInt(teamId) * 100 + 3,
        full_name: `${teamName} Player 3`,
        team_name: teamName,
        position: 'SF',
        salary: 20000000
      },
      {
        player_id: parseInt(teamId) * 100 + 4,
        full_name: `${teamName} Player 4`,
        team_name: teamName,
        position: 'PF',
        salary: 15000000
      },
      {
        player_id: parseInt(teamId) * 100 + 5,
        full_name: `${teamName} Player 5`,
        team_name: teamName,
        position: 'C',
        salary: 10000000
      }
    ]
    console.log('使用模拟球员数据:', players.value)
  } finally {
    isLoadingPlayers.value = false
  }
}

// 处理球队选择变化
const handleTeamChange = () => {
  selectedPlayerId.value = ''
  loadPlayers(selectedTeam.value)
}

// 添加球员到比较列表
const addPlayer = async () => {
  if (!selectedPlayerId.value) return
  
  try {
    isLoading.value = true
    
    // 检查球员是否已经在比较列表中
    if (comparisonPlayers.value.some(p => p.player_id === selectedPlayerId.value)) {
      alert('该球员已经在比较列表中')
      return
    }
    
    // 获取球员详细信息
    const playerInfo = players.value.find(p => p.player_id === selectedPlayerId.value)
    if (playerInfo) {
      comparisonPlayers.value.push(playerInfo)
      await loadPlayerData(playerInfo.player_id)
      updateChart()
    }
  } catch (error) {
    console.error('添加球员失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 从比较列表中删除球员
const removePlayer = (playerId) => {
  comparisonPlayers.value = comparisonPlayers.value.filter(p => p.player_id !== playerId)
  delete comparisonData.value[playerId]
  updateChart()
}

// 加载球员数据
const loadPlayerData = async (playerId) => {
  try {
    const response = await fetch(`/api/stats/player/${playerId}/game-stats`)
    if (!response.ok) {
      throw new Error('获取球员数据失败')
    }
    const data = await response.json()
    const gameStats = data.game_stats || []
    
    // 处理数据为每日一格的格式
    comparisonData.value[playerId] = processDailyGameData(gameStats)
  } catch (error) {
    console.error('加载球员数据失败:', error)
    // 如果API请求失败，使用模拟数据
    comparisonData.value[playerId] = generateMockMatchData()
  }
}

// 处理游戏数据为每日一格的格式
const processDailyGameData = (gameStats) => {
  if (!gameStats || gameStats.length === 0) {
    return { dates: [], ratings: [] }
  }
  
  // 找出日期范围
  const gameDates = gameStats.map(game => new Date(game.game_date))
  const minDate = new Date(Math.min(...gameDates))
  const maxDate = new Date(Math.max(...gameDates))
  
  // 创建日期映射
  const dateMap = {}
  gameStats.forEach(game => {
    dateMap[game.game_date] = game.score
  })
  
  // 生成完整的日期范围
  const dates = []
  const ratings = []
  const currentDate = new Date(minDate)
  
  while (currentDate <= maxDate) {
    const dateStr = currentDate.toISOString().split('T')[0]
    const displayDate = currentDate.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit'
    })
    
    dates.push(displayDate)
    // 如果当天有数据则使用数据，否则为null
    ratings.push(dateMap[dateStr] || null)
    
    // 移动到下一天
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return { dates, ratings }
}

// 模拟比赛数据
const generateMockMatchData = () => {
  const dates = []
  const ratings = []
  const today = new Date()
  
  // 生成过去30天的数据范围
  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - 29)
  
  const currentDate = new Date(startDate)
  
  while (currentDate <= today) {
    const displayDate = currentDate.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit'
    })
    dates.push(displayDate)
    
    // 随机决定当天是否有比赛（约30%的概率有比赛）
    const hasGame = Math.random() < 0.3
    if (hasGame) {
      // 生成6-10之间的随机评分
      ratings.push((Math.random() * 4 + 6).toFixed(1))
    } else {
      // 没有比赛，数据为null
      ratings.push(null)
    }
    
    // 移动到下一天
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return { dates, ratings }
}

// 颜色生成函数
const getPlayerColor = (index) => {
  const colors = [
    '#667eea', // 蓝色
    '#764ba2', // 紫色
    '#f093fb', // 粉色
    '#4facfe', // 天蓝色
    '#43e97b', // 绿色
    '#fa709a', // 红色
    '#fee140', // 黄色
    '#00f2fe', // 青色
    '#fe53bb', // 玫红色
    '#00f5d4'  // 薄荷绿
  ]
  return colors[index % colors.length]
}

// 更新图表
const updateChart = async () => {
  if (!comparisonChart.value || comparisonPlayers.value.length === 0) return
  
  try {
    // 清除之前的图表实例
    if (chartInstance.value) {
      chartInstance.value.destroy()
    }
    
    // 动态导入Chart.js及其组件
    const chartModule = await import('chart.js')
    const { Chart, LinearScale, CategoryScale, PointElement, LineElement, LineController, Title, Tooltip, Legend } = chartModule
    
    // 注册必要的组件
    Chart.register(LinearScale, CategoryScale, PointElement, LineElement, LineController, Title, Tooltip, Legend)
    
    // 准备图表数据
    const datasets = comparisonPlayers.value.map((player, index) => {
      const playerData = comparisonData.value[player.player_id]
      return {
        label: player.full_name,
        data: playerData?.ratings || [],
        borderColor: getPlayerColor(index),
        backgroundColor: `${getPlayerColor(index)}20`, // 20% opacity
        tension: 0.4,
        fill: true,
        spanGaps: true
      }
    })
    
    // 获取所有日期标签（使用第一个球员的日期作为基准）
    const labels = comparisonPlayers.value.length > 0 
      ? comparisonData.value[comparisonPlayers.value[0].player_id]?.dates || []
      : []
    
    // 计算y轴上下限 - 基于所有球员的数据点
    const allRatings = []
    comparisonPlayers.value.forEach(player => {
      const playerData = comparisonData.value[player.player_id]
      if (playerData && playerData.ratings) {
        playerData.ratings.forEach(rating => {
          if (rating !== null && !isNaN(rating)) {
            allRatings.push(parseFloat(rating))
          }
        })
      }
    })
    
    let yMin = -5
    let yMax = 30
    
    if (allRatings.length > 0) {
      const minValue = Math.min(...allRatings)
      const maxValue = Math.max(...allRatings)
      yMin = minValue - 3
      yMax = maxValue + 3
    }
    
    // 创建图表
    chartInstance.value = new Chart(comparisonChart.value, {
      type: 'line',
      data: {
        labels,
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: yMin,
            max: yMax,
            title: {
              display: true,
              text: '评分'
            }
          },
          x: {
            title: {
              display: true,
              text: '日期'
            },
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        }
      }
    })
  } catch (error) {
    console.error('更新图表失败:', error)
  }
}

// 初始化
onMounted(async () => {
  await loadTeams()
})

// 组件销毁时清理图表实例
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
.player-comparison-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.player-comparison-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

/* 选择区域样式 */
.player-selection-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.selection-controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.team-selector, .player-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.team-selector label, .player-selector label {
  font-weight: 600;
  color: #666;
  white-space: nowrap;
}

.team-selector select, .player-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 180px;
}

.add-player-btn {
  padding: 8px 16px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.add-player-btn:hover:not(:disabled) {
  background-color: #5a6fd8;
}

.add-player-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 已选球员列表 */
.selected-players {
  margin-top: 20px;
}

.selected-players h3 {
  color: #333;
  margin-bottom: 15px;
}

.players-list {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.player-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: white;
  padding: 10px 15px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-width: 200px;
}

.player-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
  border: 2px solid #667eea;
}

.player-name {
  font-weight: 600;
  color: #333;
  flex: 1;
}

.player-team {
  font-size: 12px;
  color: #666;
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
}

.remove-player-btn {
  padding: 4px 10px;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.remove-player-btn:hover:not(:disabled) {
  background-color: #ff5252;
}

.remove-player-btn:disabled {
  background-color: #ffb3b3;
  cursor: not-allowed;
}

/* 图表区域样式 */
.chart-section {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.chart-section h3 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.chart-container {
  width: 100%;
  height: 500px;
  position: relative;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #666;
  font-size: 18px;
}

/* 加载状态 */
select:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .selection-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .team-selector, .player-selector {
    width: 100%;
  }
  
  .team-selector select, .player-selector select {
    flex: 1;
    min-width: unset;
  }
  
  .player-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 150px;
  }
  
  .chart-container {
    height: 400px;
  }
}
</style>