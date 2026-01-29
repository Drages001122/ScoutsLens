<template>
  <div class="rankings-page">
    <h2>球员排行榜</h2>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="date-selector">
        <label for="date">选择日期：</label>
        <input 
          type="date" 
          id="date" 
          v-model="selectedDate" 
          @change="fetchPlayerStats"
        />
      </div>
      
      <div class="sort-control">
        <label for="sort-order">排序方式：</label>
        <select 
          id="sort-order" 
          v-model="sortOrder" 
          @change="fetchPlayerStats"
        >
          <option value="desc">评分降序</option>
          <option value="asc">评分升序</option>
        </select>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <!-- 数据展示 -->
    <div v-else-if="players.length > 0" class="stats-container">
      <div class="stats-summary">
        <p>日期：{{ selectedDate }}</p>
        <p>球员总数：{{ players.length }}</p>
      </div>
      
      <table class="players-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>球员</th>
            <th>球队</th>
            <th>评分</th>
            <th>上场时间</th>
            <th>三分</th>
            <th>两分</th>
            <th>罚球</th>
            <th>进攻篮板</th>
            <th>防守篮板</th>
            <th>助攻</th>
            <th>抢断</th>
            <th>盖帽</th>
            <th>失误</th>
            <th>犯规</th>
            <th>球队胜负</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(player, index) in players" :key="player.player_id">
            <td class="rank">{{ index + 1 }}</td>
            <td class="player-info">
              <div class="player-avatar">
                <img 
                  :src="`/player_avatars/${player.player_id}.png`" 
                  :alt="`${player.player_id}的头像`"
                  @error="handleImageError"
                />
              </div>
              <span class="player-id">{{ player.player_id }}</span>
            </td>
            <td>{{ player.team_name }}</td>
            <td class="score">{{ player.score.toFixed(2) }}</td>
            <td>{{ player.minutes }}分钟</td>
            <td>{{ player.three_pointers }}</td>
            <td>{{ player.two_pointers }}</td>
            <td>{{ player.free_throws }}</td>
            <td>{{ player.offensive_rebounds }}</td>
            <td>{{ player.defensive_rebounds }}</td>
            <td>{{ player.assists }}</td>
            <td>{{ player.steals }}</td>
            <td>{{ player.blocks }}</td>
            <td>{{ player.turnovers }}</td>
            <td>{{ player.personal_fouls }}</td>
            <td :class="player.team_won ? 'won' : 'lost'">
              {{ player.team_won ? '胜' : '负' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 无数据提示 -->
    <div v-else class="no-data">
      <p>该日期暂无数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import API_CONFIG from '../config/api.js';

const apiConfig = API_CONFIG;

// 响应式数据
const selectedDate = ref('');
const sortOrder = ref('desc');
const players = ref([]);
const loading = ref(false);
const error = ref(null);

// 初始化
onMounted(() => {
  // 设置默认日期为今天
  const today = new Date().toISOString().split('T')[0];
  selectedDate.value = today;
  // 获取数据
  fetchPlayerStats();
});

// 获取球员统计数据
const fetchPlayerStats = async () => {
  if (!selectedDate.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(
      `${apiConfig.BASE_URL}${apiConfig.ENDPOINTS.PLAYERS_GAME_STATS}?game_date=${selectedDate.value}&sort_order=${sortOrder.value}`
    );
    
    if (!response.ok) {
      throw new Error('获取数据失败');
    }
    
    const data = await response.json();
    players.value = data.players || [];
  } catch (err) {
    error.value = err.message;
    players.value = [];
  } finally {
    loading.value = false;
  }
};

// 处理头像加载失败
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/50';
};
</script>

<style scoped>
.rankings-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.control-panel {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.date-selector, .sort-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

input[type="date"], select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.error {
  color: #d9534f;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.stats-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
  font-size: 14px;
}

.players-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.players-table th,
.players-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #ddd;
}

.players-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 14px;
}

.players-table tr:hover {
  background-color: #f5f5f5;
}

.rank {
  font-weight: bold;
  width: 60px;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 120px;
}

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.player-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.player-id {
  font-size: 14px;
}

.score {
  font-weight: bold;
  color: #007bff;
  width: 80px;
}

.won {
  color: #28a745;
  font-weight: bold;
}

.lost {
  color: #dc3545;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .players-table {
    font-size: 12px;
  }
  
  .players-table th,
  .players-table td {
    padding: 8px;
  }
}

@media (max-width: 768px) {
  .control-panel {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .players-table {
    display: block;
    overflow-x: auto;
  }
}
</style>