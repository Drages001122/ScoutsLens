<template>
  <div class="rankings-page">
    <h2>球员排行榜</h2>
    
    <!-- 评分模式切换 -->
    <div class="mode-toggle">
      <div class="mode-slider" :style="{ transform: ratingMode === 'average' ? 'translateX(0)' : 'translateX(calc(100% + 4px))' }"></div>
      <button 
        :class="['mode-btn', { active: ratingMode === 'average' }]"
        @click="switchMode('average')"
      >
        场均评分
      </button>
      <button 
        :class="['mode-btn', { active: ratingMode === 'single' }]"
        @click="switchMode('single')"
      >
        单日评分
      </button>
    </div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <div v-if="ratingMode === 'single'" class="date-selector">
        <label for="date">选择日期：</label>
        <input 
          type="date" 
          id="date" 
          v-model="selectedDate" 
          @change="handleDateChange"
        />
      </div>
      
      <div class="sort-control">
        <label for="sort-field">排序字段：</label>
        <select 
          id="sort-field" 
          v-model="sortField" 
          @change="handleSortChange"
        >
          <option value="rating">评分</option>
          <option value="salary">薪资</option>
          <option value="minutes">上场时间</option>
          <option value="points">得分</option>
          <option value="offensive_rebounds">进攻篮板</option>
          <option value="defensive_rebounds">防守篮板</option>
          <option value="assists">助攻</option>
          <option value="steals">抢断</option>
          <option value="blocks">盖帽</option>
          <option value="turnovers">失误</option>
          <option value="personal_fouls">犯规</option>
          <option v-if="ratingMode === 'average'" value="games_played">出场次数</option>
          <optgroup label="三分">
            <option value="three_pointers_made">三分命中</option>
            <option value="three_pointers_attempted">三分出手</option>
            <option value="three_pointers_percentage">三分命中率</option>
          </optgroup>
          <optgroup label="两分">
            <option value="two_pointers_made">两分命中</option>
            <option value="two_pointers_attempted">两分出手</option>
            <option value="two_pointers_percentage">两分命中率</option>
          </optgroup>
          <optgroup label="罚球">
            <option value="free_throws_made">罚球命中</option>
            <option value="free_throws_attempted">罚球出手</option>
            <option value="free_throws_percentage">罚球命中率</option>
          </optgroup>
        </select>
      </div>
      
      <div class="sort-control">
        <label for="sort-order">排序方式：</label>
        <select 
          id="sort-order" 
          v-model="sortOrder" 
          @change="handleSortChange"
        >
          <option value="desc">降序</option>
          <option value="asc">升序</option>
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
            <th :class="{ 'sort-active': sortField === 'salary' }">薪资<span v-if="sortField === 'salary'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'rating' }">评分<span v-if="sortField === 'rating'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'minutes' }">上场时间<span v-if="sortField === 'minutes'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'points' }">得分<span v-if="sortField === 'points'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th>三分</th>
            <th>两分</th>
            <th>罚球</th>
            <th :class="{ 'sort-active': sortField === 'offensive_rebounds' }">进攻篮板<span v-if="sortField === 'offensive_rebounds'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'defensive_rebounds' }">防守篮板<span v-if="sortField === 'defensive_rebounds'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'assists' }">助攻<span v-if="sortField === 'assists'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'steals' }">抢断<span v-if="sortField === 'steals'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'blocks' }">盖帽<span v-if="sortField === 'blocks'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'turnovers' }">失误<span v-if="sortField === 'turnovers'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th :class="{ 'sort-active': sortField === 'personal_fouls' }">犯规<span v-if="sortField === 'personal_fouls'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th v-if="ratingMode === 'average'" :class="{ 'sort-active': sortField === 'games_played' }">出场次数<span v-if="sortField === 'games_played'" class="sort-indicator">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span></th>
            <th v-if="ratingMode === 'single'">球队胜负</th>
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
            <td class="score">{{ player.rating.toFixed(1) }}</td>
            <td>{{ formatMinutes(player.minutes) }}</td>
            <td>{{ formatNumber(player.points) }}</td>
            <td>{{ formatShootingStats(player.three_pointers_made, player.three_pointers_attempted) }}</td>
            <td>{{ formatShootingStats(player.two_pointers_made, player.two_pointers_attempted) }}</td>
            <td>{{ formatShootingStats(player.free_throws_made, player.free_throws_attempted) }}</td>
            <td>{{ formatNumber(player.offensive_rebounds) }}</td>
            <td>{{ formatNumber(player.defensive_rebounds) }}</td>
            <td>{{ formatNumber(player.assists) }}</td>
            <td>{{ formatNumber(player.steals) }}</td>
            <td>{{ formatNumber(player.blocks) }}</td>
            <td>{{ formatNumber(player.turnovers) }}</td>
            <td>{{ formatNumber(player.personal_fouls) }}</td>
            <td v-if="ratingMode === 'average'">{{ player.games_played }}</td>
            <td v-if="ratingMode === 'single'" :class="player.team_won ? 'won' : 'lost'">
              {{ player.team_won ? '胜' : '负' }}
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 翻页控件 -->
      <Pagination
        v-if="totalPages > 0"
        :current-page="currentPage"
        :total-pages="totalPages"
        :total-items="totalItems"
        :per-page="perPage"
        :per-page-options="[10, 15, 20, 25, 50]"
        @page-change="handlePageChange"
        @per-page-change="handlePerPageChange"
      />
    </div>
    
    <!-- 无数据提示 -->
    <div v-else class="no-data">
      <p>{{ ratingMode === 'single' ? '该日期暂无数据' : '暂无数据' }}</p>
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
import Pagination from '../components/Pagination.vue';

const apiConfig = API_CONFIG;

// 响应式数据
const ratingMode = ref('average');
const selectedDate = ref('');
const sortField = ref('rating');
const sortOrder = ref('desc');
const players = ref([]);
const loading = ref(false);
const error = ref(null);
const currentPage = ref(1);
const perPage = ref(10);
const totalPages = ref(1);
const totalItems = ref(0);
const showPlayerProfile = ref(false);
const selectedPlayer = ref(null);

const savedSortSettings = {
  average: { field: 'rating', order: 'desc' },
  single: { field: 'rating', order: 'desc' }
};

// 初始化
onMounted(() => {
  const today = new Date().toISOString().split('T')[0];
  selectedDate.value = today;
  fetchPlayerStats();
});

// 切换评分模式
const switchMode = (mode) => {
  savedSortSettings[ratingMode.value] = {
    field: sortField.value,
    order: sortOrder.value
  };
  ratingMode.value = mode;
  const settings = savedSortSettings[mode];
  sortField.value = settings.field;
  sortOrder.value = settings.order;
  currentPage.value = 1;
  fetchPlayerStats();
};

// 获取球员统计数据
const fetchPlayerStats = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    let url;
    
    if (ratingMode.value === 'average') {
      url = `${apiConfig.ENDPOINTS.STATS}/average-stats?sort_by=${sortField.value}&sort_order=${sortOrder.value}&page=${currentPage.value}&per_page=${perPage.value}`;
    } else {
      if (!selectedDate.value) {
        throw new Error('请选择日期');
      }
      url = `${apiConfig.ENDPOINTS.STATS}/game-stats?game_date=${selectedDate.value}&sort_by=${sortField.value}&sort_order=${sortOrder.value}&page=${currentPage.value}&per_page=${perPage.value}`;
    }
    
    const response = await fetch(url);
    
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

const handlePageChange = (page) => {
  currentPage.value = page;
  fetchPlayerStats();
};

const handlePerPageChange = (newPerPage) => {
  perPage.value = newPerPage;
  currentPage.value = 1;
  fetchPlayerStats();
};

// 处理头像加载失败
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/50';
};

// 格式化上场时间为整数分钟
const formatMinutes = (minutes) => {
  const mins = Math.floor(minutes);
  return mins.toString();
};

// 格式化数字，场均模式保留一位小数，单日模式显示整数
const formatNumber = (num) => {
  if (ratingMode.value === 'average') {
    return num.toFixed(1);
  }
  return Math.round(num).toString();
};

// 格式化投篮统计为 {命中数}/{出手数} 格式
const formatShootingStats = (made, attempted) => {
  if (ratingMode.value === 'average') {
    return `${made.toFixed(1)}/${attempted.toFixed(1)}`;
  }
  return `${Math.round(made)}/${Math.round(attempted)}`;
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

.mode-toggle {
  display: inline-flex;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  padding: 4px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  position: relative;
}

.mode-slider {
  position: absolute;
  top: 4px;
  bottom: 4px;
  width: calc(50% - 6px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 0;
}

.mode-btn {
  position: relative;
  padding: 12px 32px;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.mode-btn:hover {
  color: #475569;
}

.mode-btn.active {
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.control-panel {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
  flex-wrap: wrap;
}

.date-selector, .sort-control, .per-page-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-selector label, .sort-control label, .per-page-control label {
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

input[type="date"], select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  min-width: 120px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input[type="date"]:hover, select:hover {
  border-color: #007bff;
}

input[type="date"]:focus, select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

select optgroup {
  font-weight: 600;
  color: #666;
  background-color: #f8f9fa;
}

select option {
  padding: 8px;
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

.sort-active {
  background-color: #e3f2fd !important;
  color: #1976d2 !important;
  font-weight: 700;
}

.sort-indicator {
  margin-left: 4px;
  font-size: 12px;
  color: #1976d2;
}

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
