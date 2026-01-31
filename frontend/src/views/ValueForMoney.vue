<template>
  <div class="value-for-money">
    <h1>球员性价比分析</h1>
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

const chartCanvas = ref(null)
let chartInstance = null

const fetchPlayerData = async () => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/stats/value-for-money`)
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
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
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
              return [
                `球员: ${point.player_name}`,
                `球队: ${translateTeam(point.team_name)}`,
                `位置: ${translatePosition(point.position)}`,
                `薪资: ${point.x}`,
                `平均评分: ${point.y.toFixed(2)}`,
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
          text: '球员薪资 vs 平均评分'
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
            text: '平均评分'
          }
        }
      }
    }
  })
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