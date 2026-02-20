<template>
  <div class="player-profile-overlay" v-if="visible" @click="close">
    <div class="player-profile-content" @click.stop>
      <div class="player-profile-header">
        <h2>{{ player?.full_name }}</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="player-profile-body">
        <div class="player-info-section">
          <div class="player-avatar-container">
            <img 
              :src="`/player_avatars/${player?.player_id}.png`" 
              :alt="player?.full_name" 
              class="player-avatar-large"
              onerror="this.src='https://via.placeholder.com/120'"
            >
          </div>
          <div class="player-details">
            <div class="basic-info">
              <div class="detail-item">
                <span class="detail-label">球队：</span>
                <span class="detail-value">{{ translateTeam(player?.team_name) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">位置：</span>
                <span class="detail-value">{{ translatePosition(player?.position) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">薪资：</span>
                <span class="detail-value">${{ player?.salary?.toLocaleString() }}</span>
              </div>
            </div>
            <div v-if="averageStats" class="average-stats-container">
              <div class="stats-header">
                <div class="stat-cell">场均得分</div>
                <div class="stat-cell">场均篮板</div>
                <div class="stat-cell">场均助攻</div>
                <div class="stat-cell">场均抢断</div>
                <div class="stat-cell">场均盖帽</div>
                <div class="stat-cell">场均失误</div>
                <div class="stat-cell">场均时间</div>
                <div class="stat-cell">投篮命中率</div>
                <div class="stat-cell">三分命中率</div>
                <div class="stat-cell">罚球命中率</div>
                <div class="stat-cell">比赛场次</div>
              </div>
              <div class="stats-values">
                <div class="stat-cell">{{ averageStats.points_per_game }}</div>
                <div class="stat-cell">{{ averageStats.rebounds_per_game }}</div>
                <div class="stat-cell">{{ averageStats.assists_per_game }}</div>
                <div class="stat-cell">{{ averageStats.steals_per_game }}</div>
                <div class="stat-cell">{{ averageStats.blocks_per_game }}</div>
                <div class="stat-cell">{{ averageStats.turnovers_per_game }}</div>
                <div class="stat-cell">{{ averageStats.minutes_per_game }}分钟</div>
                <div class="stat-cell">{{ averageStats.field_goal_percentage }}%</div>
                <div class="stat-cell">{{ averageStats.three_point_percentage }}%</div>
                <div class="stat-cell">{{ averageStats.free_throw_percentage }}%</div>
                <div class="stat-cell">{{ averageStats.games_played }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="player-stats-section">
          <h3>本赛季比赛评分</h3>
          <div class="chart-container">
            <canvas ref="ratingChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { translateTeam, translatePosition } from '../utils/translation'
import { Chart, LinearScale, CategoryScale, PointElement, LineElement, LineController, Title, Tooltip, Legend } from 'chart.js/auto'

Chart.register(LinearScale, CategoryScale, PointElement, LineElement, LineController, Title, Tooltip, Legend)

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  player: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close'])

// Refs
const ratingChart = ref(null)
const chartInstance = ref(null)
const averageStats = ref(null)

// 关闭弹窗
const close = () => {
  emit('close')
}

// 加载场均数据
const loadAverageStats = async () => {
  if (!props.player) return
  
  try {
    const url = `/api/stats/player/${props.player.player_id}/average-stats`
    const response = await fetch(url)
    
    if (!response.ok) {
      console.error('获取场均数据失败')
      return
    }
    
    const data = await response.json()
    averageStats.value = data
  } catch (error) {
    console.error('加载场均数据失败:', error)
  }
}

// 计算球员评分平均值
const calculatePlayerAverage = (ratings) => {
  const validRatings = ratings.filter(rating => rating !== null && !isNaN(rating))
  if (validRatings.length === 0) return 0
  
  const sum = validRatings.reduce((acc, rating) => acc + parseFloat(rating), 0)
  return sum / validRatings.length
}

// 加载图表
const loadChart = async () => {
  if (!props.player || !ratingChart.value) return
  
  console.log('开始加载图表，球员信息:', props.player)
  
  // 清除之前的图表实例
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
  
  try {
    // 从API获取球员比赛数据
    const url = `/api/stats/player/${props.player.player_id}/game-stats`
    console.log('请求URL:', url)
    const response = await fetch(url)
    
    console.log('响应状态:', response.status)
    
    if (!response.ok) {
      throw new Error('获取比赛数据失败')
    }
    
    const data = await response.json()
    console.log('返回的数据:', data)
    const gameStats = data.game_stats || []
    
    // 准备图表数据 - 处理为每日一格的格式
    let matchData
    matchData = processDailyGameData(gameStats)
    
    console.log('图表数据 - 日期:', matchData.dates)
    console.log('图表数据 - 评分:', matchData.ratings)
    
    // 计算平均值
    const average = calculatePlayerAverage(matchData.ratings)
    console.log('球员平均值:', average)
    
    // 准备数据集
    const datasets = [{
      label: '比赛评分',
      data: matchData.ratings,
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      tension: 0.4,
      fill: true,
      spanGaps: true
    }]
    
    // 添加平均值水平线
    if (average !== 0 && !isNaN(average)) {
      datasets.push({
        label: '平均值',
        data: Array(matchData.dates.length).fill(average),
        borderColor: '#667eea',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
        tension: 0
      })
    }
    
    // 计算y轴上下限
    const validRatings = matchData.ratings.filter(rating => rating !== null && !isNaN(rating))
    let yMin = -5
    let yMax = 30
    
    if (validRatings.length > 0) {
      const minValue = Math.min(...validRatings)
      const maxValue = Math.max(...validRatings)
      yMin = minValue - 3
      yMax = maxValue + 3
    }
    
    // 创建图表
    chartInstance.value = new Chart(ratingChart.value, {
      type: 'line',
      data: {
        labels: matchData.dates,
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
        }
      }
    })
  } catch (error) {
    console.error('加载图表失败:', error)
    // 如果API请求失败，使用模拟数据
    try {
      const matchData = generateMockMatchData()
      const average = calculatePlayerAverage(matchData.ratings)
      console.log('模拟数据平均值:', average)
      
      // 准备数据集
      const datasets = [{
        label: '比赛评分',
        data: matchData.ratings,
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
        spanGaps: false
      }]
      
      // 添加平均值水平线
      if (average !== 0 && !isNaN(average)) {
        datasets.push({
          label: '平均值',
          data: Array(matchData.dates.length).fill(average),
          borderColor: '#667eea',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false,
          tension: 0
        })
      }
      
      // 计算y轴上下限
      const validRatings = matchData.ratings.filter(rating => rating !== null && !isNaN(rating))
      let yMin = -5
      let yMax = 30
      
      if (validRatings.length > 0) {
        const minValue = Math.min(...validRatings)
        const maxValue = Math.max(...validRatings)
        yMin = minValue - 3
        yMax = maxValue + 3
      }
      
      chartInstance.value = new Chart(ratingChart.value, {
        type: 'line',
        data: {
          labels: matchData.dates,
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
          }
        }
      })
    } catch (innerError) {
      console.error('加载模拟数据失败:', innerError)
    }
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
    dateMap[game.game_date] = game.rating
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

// 监听visible和player变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    loadAverageStats()
    setTimeout(loadChart, 100)
  }
})

watch(() => props.player, () => {
  if (props.visible) {
    loadAverageStats()
    loadChart()
  }
})

// 组件销毁时清理图表实例
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
.player-profile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.player-profile-content {
  background-color: white;
  border-radius: 12px;
  width: 90vw;
  height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.player-profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
  border-radius: 12px 12px 0 0;
}

.player-profile-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
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

.player-profile-body {
  padding: 20px;
}

.player-info-section {
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
  align-items: flex-start;
}

.player-avatar-container {
  flex-shrink: 0;
}

.player-avatar-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
  border: 4px solid #667eea;
}

.player-details {
  flex: 1;
  display: flex;
  gap: 40px;
}

.basic-info {
  min-width: 200px;
}

.detail-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.detail-label {
  font-weight: 600;
  color: #666;
  width: 80px;
  font-size: 14px;
}

.detail-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.average-stats-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stats-header,
.stats-values {
  display: flex;
  gap: 2px;
}

.stat-cell {
  flex: 1;
  padding: 8px 10px;
  text-align: center;
  min-width: 80px;
  font-size: 12px;
}

.stats-header {
  background-color: #4a5568;
  color: white;
  border-radius: 6px 6px 0 0;
  font-weight: 600;
}

.stats-values {
  background-color: #f8f9fa;
  border-radius: 0 0 6px 6px;
}

.stats-values .stat-cell {
  font-weight: 500;
  color: #333;
}

.player-stats-section {
  margin-top: 30px;
}

.player-stats-section h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
}

.chart-container {
  width: 100%;
  height: 450px;
  position: relative;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .player-info-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .player-details {
    flex-direction: column;
    gap: 20px;
  }
  
  .basic-info {
    min-width: auto;
  }
  
  .stats-header,
  .stats-values {
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .stat-cell {
    min-width: 70px;
    padding: 6px 8px;
    font-size: 11px;
  }
  
  .detail-item {
    justify-content: center;
  }
  
  .detail-label {
    width: auto;
    margin-right: 10px;
  }
  
  .player-profile-content {
    width: 90vw;
    height: 90vh;
    margin: 0;
  }
}
</style>