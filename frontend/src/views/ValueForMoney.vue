<template>
  <div class="value-for-money">
    <h1>球员性价比分析</h1>
    <div class="controls">
      <div class="control-group">
        <label for="viewType">查看方式：</label>
        <select id="viewType" v-model="viewType" @change="handleViewTypeChange">
          <option value="average">平均评分</option>
          <option value="date">按日期查看</option>
        </select>
      </div>
      <div class="control-group" v-if="viewType === 'date'">
        <label for="gameDate">选择日期：</label>
        <input type="date" id="gameDate" v-model="gameDate" @change="handleDateChange">
      </div>
    </div>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Chart from 'chart.js/auto'
import API_CONFIG from '../config/api'
import { translateTeam, translatePosition } from '../utils/translation'

// 格式化薪资函数，显示为$开头且3位一个逗号的形式
const formatSalary = (salary) => {
  return '$' + salary.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const chartCanvas = ref(null)
let chartInstance = null
const viewType = ref('average')
const gameDate = ref('')

const fetchPlayerData = async () => {
  try {
    let url = `${API_CONFIG.BASE_URL}/api/stats/value-for-money`
    if (viewType.value === 'date' && gameDate.value) {
      url += `?game_date=${gameDate.value}`
    }
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('Failed to fetch player data')
    }
    const data = await response.json()
    return data.players
  } catch (error) {
    console.error('Error fetching player data:', error)
    return []
  }
}

const createChart = (playerData) => {
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  
  const chartTitle = viewType.value === 'average' 
    ? '球员薪资 vs 平均评分' 
    : `球员薪资 vs ${gameDate.value}评分`
  
  const yAxisTitle = viewType.value === 'average' 
    ? '平均评分' 
    : '当日评分'
  
  chartInstance = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: '球员性价比',
        data: playerData.map(player => ({
          x: player.salary,
          y: player.average_rating,
          player_name: player.player_name,
          team_name: player.team_name,
          position: player.position,
          salary_rank: player.salary_rank,
          rating_rank: player.rating_rank
        })),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        pointRadius: 5,
        pointHoverRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const point = context.raw
              const ratingLabel = viewType.value === 'average' 
                ? '平均评分' 
                : `当日评分`
              return [
                `球员: ${point.player_name}`,
                `球队: ${translateTeam(point.team_name)}`,
                `位置: ${translatePosition(point.position)}`,
                `薪资: ${formatSalary(point.x)}`,
                `${ratingLabel}: ${point.y.toFixed(2)}`,
                `薪资排名: ${point.salary_rank || '-'}`,
                `评分排名: ${point.rating_rank || '-'}`
              ]
            }
          }
        },
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: chartTitle
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '球员薪资'
          }
        },
        y: {
          title: {
            display: true,
            text: yAxisTitle
          }
        }
      }
    }
  })
}

const handleViewTypeChange = async () => {
  if (viewType.value === 'average') {
    const playerData = await fetchPlayerData()
    createChart(playerData)
  }
}

const handleDateChange = async () => {
  if (gameDate.value) {
    const playerData = await fetchPlayerData()
    createChart(playerData)
  }
}

onMounted(async () => {
  const playerData = await fetchPlayerData()
  createChart(playerData)
})
</script>

<style scoped>
.value-for-money {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-group label {
  font-weight: bold;
  color: #333;
}

.control-group select,
.control-group input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.chart-container {
  flex: 1;
  position: relative;
  width: 100%;
  min-height: 80vh;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}
</style>