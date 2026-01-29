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
          @change="handleDateChange"
        />
      </div>
      
      <div class="sort-control">
        <label for="sort-order">排序方式：</label>
        <select 
          id="sort-order" 
          v-model="sortOrder" 
          @change="handleSortChange"
        >
          <option value="desc">评分降序</option>
          <option value="asc">评分升序</option>
        </select>
      </div>
      
      <div class="per-page-control">
        <label for="per-page">每页显示：</label>
        <select 
          id="per-page" 
          v-model="perPage" 
          @change="handlePerPageChange"
        >
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
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
      <table class="players-table">
        <thead>
          <tr>
            <th>排名</th>
            <th></th>
            <th>球员</th>
            <th>球队</th>
            <th>位置</th>
            <th>薪资</th>
            <th>评分</th>
            <th>上场时间</th>
            <th>得分</th>
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
            <td class="rank">{{ (currentPage - 1) * perPage + index + 1 }}</td>
            <td class="player-avatar">
              <img 
                :src="`/player_avatars/${player.player_id}.png`" 
                :alt="`${player.player_name}的头像`"
                @error="handleImageError"
                @click="openPlayerProfile(player)"
                style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
                @mouseover="$event.target.style.transform = 'scale(1.1)'; $event.target.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)'"
                @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
              />
            </td>
            <td class="player-name">{{ player.player_name }}</td>
            <td>{{ translations.teams[player.team_name] || player.team_name }}</td>
            <td>{{ translatePosition(player.position) }}</td>
            <td>${{ player.salary.toLocaleString() }}</td>
            <td class="score">{{ player.score.toFixed(1) }}</td>
            <td>{{ formatMinutes(player.minutes) }}</td>
            <td>{{ player.points }}</td>
            <td>{{ formatShootingStats(player.three_pointers_made, player.three_pointers_attempted) }}</td>
            <td>{{ formatShootingStats(player.two_pointers_made, player.two_pointers_attempted) }}</td>
            <td>{{ formatShootingStats(player.free_throws_made, player.free_throws_attempted) }}</td>
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
      
      <!-- 翻页控件 -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="pagination-btn" 
          @click="goToFirstPage" 
          :disabled="currentPage === 1"
        >
          首页
        </button>
        <button 
          class="pagination-btn" 
          @click="goToPreviousPage" 
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ totalItems }} 条)
        </span>
        <button 
          class="pagination-btn" 
          @click="goToNextPage" 
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
        <button 
          class="pagination-btn" 
          @click="goToLastPage" 
          :disabled="currentPage === totalPages"
        >
          末页
        </button>
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-else class="no-data">
      <p>该日期暂无数据</p>
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
import { ref, onMounted } from 'vue';
import API_CONFIG from '../config/api.js';
import translations from '../data/translations.json';
import { translatePosition } from '../utils/translation';
import PlayerProfile from '../components/PlayerProfile.vue';

const apiConfig = API_CONFIG;

// 响应式数据
const selectedDate = ref('');
const sortOrder = ref('desc');
const players = ref([]);
const loading = ref(false);
const error = ref(null);
const currentPage = ref(1);
const perPage = ref(10);
const totalPages = ref(1);
const totalItems = ref(0);
// 球员个人介绍相关状态
const showPlayerProfile = ref(false);
const selectedPlayer = ref(null);

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
      `${apiConfig.BASE_URL}${apiConfig.ENDPOINTS.PLAYERS_GAME_STATS}?game_date=${selectedDate.value}&sort_order=${sortOrder.value}&page=${currentPage.value}&per_page=${perPage.value}`
    );
    
    if (!response.ok) {
      throw new Error('获取数据失败');
    }
    
    const data = await response.json();
    players.value = data.players || [];
    if (data.pagination) {
      totalPages.value = data.pagination.total_pages;
      totalItems.value = data.pagination.total_items;
    }
  } catch (err) {
    error.value = err.message;
    players.value = [];
  } finally {
    loading.value = false;
  }
};

// 监听日期和排序变化，重置页码
const handleDateChange = () => {
  currentPage.value = 1;
  fetchPlayerStats();
};

const handleSortChange = () => {
  currentPage.value = 1;
  fetchPlayerStats();
};

const handlePerPageChange = () => {
  currentPage.value = 1;
  fetchPlayerStats();
};

// 处理头像加载失败
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/50';
};

// 格式化上场时间为 xx:xx 格式
const formatMinutes = (minutes) => {
  const mins = Math.floor(minutes);
  const secs = Math.round((minutes - mins) * 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

// 格式化投篮统计为 {命中数}/{出手数} 格式
const formatShootingStats = (made, attempted) => {
  return `${made}/${attempted}`;
};

// 翻页函数
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchPlayerStats();
};

const goToFirstPage = () => {
  currentPage.value = 1;
  fetchPlayerStats();
};

const goToLastPage = () => {
  currentPage.value = totalPages.value;
  fetchPlayerStats();
};

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchPlayerStats();
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchPlayerStats();
  }
};

// 打开球员个人介绍弹窗
const openPlayerProfile = (player) => {
  selectedPlayer.value = {
    ...player,
    full_name: player.player_name
  };
  showPlayerProfile.value = true;
};

// 关闭球员个人介绍弹窗
const closePlayerProfile = () => {
  showPlayerProfile.value = false;
  selectedPlayer.value = null;
};
</script>

<style scoped>
.rankings-page {
  padding: 20px;
  width: 100%;
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

.date-selector, .sort-control, .per-page-control {
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

.player-avatar {
  width: 60px;
  text-align: center;
}

.player-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.player-name {
  font-size: 14px;
  width: 100px;
  text-align: left;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #007bff;
  color: #fff;
  border-color: #007bff;
}

.pagination-btn:disabled {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #333;
  font-weight: 500;
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
  
  .pagination {
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .pagination-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .page-info {
    font-size: 12px;
  }
}
</style>