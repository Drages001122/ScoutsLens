<template>
  <div class="lineup-ratings">
    <h2>阵容评分</h2>
    
    <!-- 日期选择器 -->
    <div class="date-selector">
      <label for="date">选择日期：</label>
      <input 
        type="date" 
        id="date" 
        v-model="selectedDate"
        @change="fetchLineups"
      >
    </div>
    
    <!-- 今日最佳阵容 -->
    <div class="best-lineup-section">
      <h3>今日最佳阵容</h3>
      <div v-if="bestLineupLoading" class="loading">加载中...</div>
      <div v-else-if="bestLineupError" class="error">{{ bestLineupError }}</div>
      <div v-else-if="bestLineup" class="best-lineup-content">
        <div class="best-lineup-header">
          <span class="total-rating">总评分：{{ bestLineup.total_rating.toFixed(1) }}</span>
          <span class="total-salary">总薪资：{{ bestLineup.total_salary.toLocaleString() }}</span>
        </div>
        
        <!-- 首发球员 -->
        <div class="players-section">
          <h4>首发球员</h4>
          <div class="stats-container">
            <table class="players-table">
              <thead>
                <tr>
                  <th>头像</th>
                  <th>球员</th>
                  <th>球队</th>
                  <th>位置</th>
                  <th>薪资</th>
                  <th>槽位</th>
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
                <tr v-for="player in bestLineup.players.filter(p => p.is_starting)" :key="player.player_id">
                  <td class="player-avatar">
                    <img 
                      :src="`/player_avatars/${player.player_id}.png`" 
                      :alt="player.full_name"
                      @error="handleImageError"
                      @click="openPlayerProfile(player)"
                      style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
                      @mouseover="$event.target.style.transform = 'scale(1.1)'; $event.target.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)'"
                      @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
                    >
                  </td>
                  <td class="player-name">{{ player.full_name }}</td>
                  <td>{{ translateTeam(player.team_name) }}</td>
                  <td>{{ translatePosition(player.position) }}</td>
                  <td>${{ player.salary.toLocaleString() }}</td>
                  <td class="player-slot">{{ player.slot }}</td>
                  <td class="score">{{ player.rating ? player.rating.toFixed(1) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.minutes ? this.formatMinutes(this.playerStats[player.player_id].minutes) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.points || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.three_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].three_pointers_made, this.playerStats[player.player_id].three_pointers_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.two_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].two_pointers_made, this.playerStats[player.player_id].two_pointers_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.free_throws_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].free_throws_made, this.playerStats[player.player_id].free_throws_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.offensive_rebounds || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.defensive_rebounds || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.assists || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.steals || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.blocks || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.turnovers || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.personal_fouls || '0' }}</td>
                  <td :class="this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? 'won' : 'lost') : ''">
                    {{ this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? '胜' : '负') : '0' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- 替补球员 -->
        <div class="players-section">
          <h4>替补球员</h4>
          <div class="stats-container">
            <table class="players-table">
              <thead>
                <tr>
                  <th>头像</th>
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
                <tr v-for="player in bestLineup.players.filter(p => !p.is_starting)" :key="player.player_id">
                  <td class="player-avatar">
                    <img 
                      :src="`/player_avatars/${player.player_id}.png`" 
                      :alt="player.full_name"
                      @error="handleImageError"
                      @click="openPlayerProfile(player)"
                      style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
                      @mouseover="$event.target.style.transform = 'scale(1.1)'; $event.target.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)'"
                      @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
                    >
                  </td>
                  <td class="player-name">{{ player.full_name }}</td>
                  <td>{{ translateTeam(player.team_name) }}</td>
                  <td>{{ translatePosition(player.position) }}</td>
                  <td>${{ player.salary.toLocaleString() }}</td>
                  <td class="score">{{ player.rating ? player.rating.toFixed(1) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.minutes ? this.formatMinutes(this.playerStats[player.player_id].minutes) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.points || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.three_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].three_pointers_made, this.playerStats[player.player_id].three_pointers_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.two_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].two_pointers_made, this.playerStats[player.player_id].two_pointers_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.free_throws_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].free_throws_made, this.playerStats[player.player_id].free_throws_attempted) : '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.offensive_rebounds || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.defensive_rebounds || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.assists || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.steals || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.blocks || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.turnovers || '0' }}</td>
                  <td>{{ this.playerStats[player.player_id]?.personal_fouls || '0' }}</td>
                  <td :class="this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? 'won' : 'lost') : ''">
                    {{ this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? '胜' : '负') : '0' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div v-else-if="!bestLineupLoading && !bestLineupError" class="no-best-lineup">
        <p>无法获取今日最佳阵容，可能是因为今日没有比赛或数据不足</p>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载中...</div>
    
    <!-- 错误信息 -->
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <!-- 阵容列表 -->
    <div v-else-if="lineups.length > 0" class="lineup-list">
      <h3>{{ selectedDate }} 的阵容</h3>
      <div class="shutter-container">
        <div 
          v-for="lineup in lineups" 
          :key="lineup.id" 
          class="shutter-item"
        >
          <div class="shutter-content" @click="toggleLineupDetails(lineup.id)">
            <div class="shutter-header">
              <span class="username">用户：{{ lineup.username }}</span>
              <span class="salary">总薪资：{{ lineup.total_salary.toLocaleString() }}</span>
              <span class="total-score">总评分：{{ calculateLineupScore(lineup).toFixed(1) }}</span>
            </div>
            <div class="shutter-footer">
              <span class="created-at">{{ formatDate(lineup.created_at) }}</span>
              <span class="toggle-icon">{{ expandedLineupId === lineup.id ? '▼' : '▶' }}</span>
            </div>
          </div>
          
          <!-- 折叠的阵容详情 -->
          <div v-if="expandedLineupId === lineup.id" class="lineup-details">
            <div class="lineup-info">
              <span class="username">用户：{{ lineup.username }}</span>
              <span class="salary">总薪资：{{ lineup.total_salary.toLocaleString() }}</span>
              <span class="total-score">总评分：{{ calculateLineupScore(lineup).toFixed(1) }}</span>
              <span class="created-at">{{ formatDate(lineup.created_at) }}</span>
            </div>
            
            <!-- 权限提示 -->
            <div v-if="!lineup.can_view" class="permission-warning">
              <p>⏰ 该阵容需要在北京时间当天早晨7:00之后才能查看</p>
            </div>
            
            <!-- 球员列表 -->
            <template v-else>
              <!-- 首发球员 -->
              <div class="players-section">
                <h4>首发球员</h4>
                <div class="stats-container">
                  <table class="players-table">
                    <thead>
                      <tr>
                        <th>头像</th>
                        <th>球员</th>
                        <th>球队</th>
                        <th>位置</th>
                        <th>薪资</th>
                        <th>槽位</th>
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
                      <tr v-for="player in lineup.players.filter(p => p.is_starting)" :key="player.id">
                        <td class="player-avatar">
                          <img 
                            :src="`/player_avatars/${player.player_id}.png`" 
                            :alt="player.full_name"
                            @error="handleImageError"
                            @click="openPlayerProfile(player)"
                            style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
                            @mouseover="$event.target.style.transform = 'scale(1.1)'; $event.target.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)'"
                            @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
                          >
                        </td>
                        <td class="player-name">{{ player.full_name }}</td>
                        <td>{{ translateTeam(player.team_name) }}</td>
                        <td>{{ translatePosition(player.position) }}</td>
                        <td>${{ player.salary.toLocaleString() }}</td>
                        <td class="player-slot">{{ player.slot }}</td>
                        <td class="score">{{ this.playerStats[player.player_id]?.rating ? this.playerStats[player.player_id].rating.toFixed(1) : '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.minutes ? this.formatMinutes(this.playerStats[player.player_id].minutes) : '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.points || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.three_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].three_pointers_made, this.playerStats[player.player_id].three_pointers_attempted) : '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.two_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].two_pointers_made, this.playerStats[player.player_id].two_pointers_attempted) : '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.free_throws_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].free_throws_made, this.playerStats[player.player_id].free_throws_attempted) : '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.offensive_rebounds || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.defensive_rebounds || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.assists || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.steals || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.blocks || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.turnovers || '0' }}</td>
                        <td>{{ this.playerStats[player.player_id]?.personal_fouls || '0' }}</td>
                        <td :class="this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? 'won' : 'lost') : ''">
                          {{ this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? '胜' : '负') : '0' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <!-- 替补球员 -->
              <div v-if="lineup.players.filter(p => !p.is_starting).length > 0" class="players-section">
              <h4>替补球员</h4>
              <div class="stats-container">
                <table class="players-table">
                  <thead>
                    <tr>
                      <th>头像</th>
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
                    <tr v-for="player in lineup.players.filter(p => !p.is_starting)" :key="player.id">
                      <td class="player-avatar">
                        <img 
                          :src="`/player_avatars/${player.player_id}.png`" 
                          :alt="player.full_name"
                          @error="handleImageError"
                          @click="openPlayerProfile(player)"
                          style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;"
                          @mouseover="$event.target.style.transform = 'scale(1.1)'; $event.target.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)'"
                          @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
                        >
                      </td>
                      <td class="player-name">{{ player.full_name }}</td>
                      <td>{{ translateTeam(player.team_name) }}</td>
                      <td>{{ translatePosition(player.position) }}</td>
                      <td>${{ player.salary.toLocaleString() }}</td>
                      <td class="score">{{ this.playerStats[player.player_id]?.rating ? this.playerStats[player.player_id].rating.toFixed(1) : '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.minutes ? this.formatMinutes(this.playerStats[player.player_id].minutes) : '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.points || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.three_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].three_pointers_made, this.playerStats[player.player_id].three_pointers_attempted) : '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.two_pointers_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].two_pointers_made, this.playerStats[player.player_id].two_pointers_attempted) : '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.free_throws_made !== undefined ? this.formatShootingStats(this.playerStats[player.player_id].free_throws_made, this.playerStats[player.player_id].free_throws_attempted) : '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.offensive_rebounds || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.defensive_rebounds || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.assists || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.steals || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.blocks || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.turnovers || '0' }}</td>
                      <td>{{ this.playerStats[player.player_id]?.personal_fouls || '0' }}</td>
                      <td :class="this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? 'won' : 'lost') : ''">
                        {{ this.playerStats[player.player_id]?.team_won !== undefined ? (this.playerStats[player.player_id].team_won ? '胜' : '负') : '0' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            </template>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 无阵容时的提示 -->
    <div v-else-if="lineups.length === 0" class="no-lineups">
      <p>该日期暂无阵容</p>
    </div>
    
    <!-- 球员个人介绍弹窗 -->
    <PlayerProfile 
      :visible="showPlayerProfile"
      :player="selectedPlayer"
      @close="closePlayerProfile"
    />
  </div>
</template>

<script>
import PlayerProfile from '../components/PlayerProfile.vue';
import API_CONFIG from '../config/api.js';
import { translateTeam, translatePosition } from '../utils/translation.js';

const apiConfig = API_CONFIG;

export default {
  name: 'LineupRatings',
  data() {
    return {
      selectedDate: new Date().toISOString().split('T')[0],
      lineups: [],
      loading: false,
      error: null,
      expandedLineupId: null,
      playerStats: {}, // 存储球员统计数据，格式：{playerId: stats}
      // 今日最佳阵容相关状态
      bestLineup: null,
      bestLineupLoading: false,
      bestLineupError: null,
      // 球员个人介绍相关状态
      showPlayerProfile: false,
      selectedPlayer: null
    }
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    }
  },
  mounted() {
    this.fetchLineups()
    this.fetchBestLineup()
  },
  methods: {
    translateTeam,
    translatePosition,
    fetchLineups() {
      this.loading = true
      this.error = null
      
      fetch(`${apiConfig.BASE_URL}/api/lineup/by-date?date=${this.selectedDate}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('获取阵容失败')
        }
        return response.json()
      })
      .then(data => {
        this.lineups = data.lineups
        this.loading = false
        // 获取球员统计数据用于排序
        this.fetchPlayerStats()
      })
      .catch(error => {
        this.error = error.message
        this.loading = false
      })
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      // 加上 8 小时（UTC+8 时区）
      date.setHours(date.getHours() + 8)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    toggleLineupDetails(lineupId) {
      this.expandedLineupId = this.expandedLineupId === lineupId ? null : lineupId
      if (this.expandedLineupId === lineupId) {
        this.fetchPlayerStats()
      }
    },
    fetchPlayerStats() {
      // 获取选中日期的球员统计数据
      fetch(`${apiConfig.BASE_URL}/api/stats/game-stats?game_date=${this.selectedDate}&per_page=1000`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('获取球员统计数据失败')
        }
        return response.json()
      })
      .then(data => {
        // 构建球员统计数据映射
        const statsMap = {}
        if (data.players) {
          data.players.forEach(player => {
            statsMap[player.player_id] = player
          })
        }
        this.playerStats = statsMap
        
        // 按照阵容总评分由高到低排序
        this.lineups.sort((a, b) => {
          const scoreA = this.calculateLineupScore(a)
          const scoreB = this.calculateLineupScore(b)
          return scoreB - scoreA
        })
      })
      .catch(error => {
        console.error('获取球员统计数据失败:', error)
      })
    },
    handleImageError(event) {
      // 图片加载失败时的处理
      console.log('头像加载失败:', event.target.src)
      // 可以设置一个内联的默认头像样式
      event.target.style.backgroundColor = '#e0e0e0'
      event.target.style.display = 'block'
    },
    formatMinutes(minutes) {
      const mins = Math.floor(minutes)
      return mins.toString()
    },
    formatShootingStats(made, attempted) {
      return `${made}/${attempted}`
    },
    calculateLineupScore(lineup) {
      const startingPlayersScore = lineup.players
        .filter(p => p.is_starting)
        .reduce((total, player) => {
          const rating = Number(this.playerStats[player.player_id]?.rating) || 0
          return total + rating
        }, 0) * 2
      
      const benchPlayersScore = lineup.players
        .filter(p => !p.is_starting)
        .reduce((total, player) => {
          const rating = Number(this.playerStats[player.player_id]?.rating) || 0
          return total + rating
        }, 0)
      
      return startingPlayersScore + benchPlayersScore
    },
    // 打开球员个人介绍弹窗
    openPlayerProfile(player) {
      this.selectedPlayer = player;
      this.showPlayerProfile = true;
    },
    // 关闭球员个人介绍弹窗
    closePlayerProfile() {
      this.showPlayerProfile = false;
      this.selectedPlayer = null;
    },
    // 获取今日最佳阵容
    fetchBestLineup() {
      this.bestLineupLoading = true;
      this.bestLineupError = null;
      
      fetch(`${apiConfig.BASE_URL}/api/lineup/best`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('获取今日最佳阵容失败');
        }
        return response.json();
      })
      .then(data => {
        this.bestLineup = data.best_lineup;
        this.bestLineupLoading = false;
        // 获取球员统计数据
        this.fetchPlayerStats();
      })
      .catch(error => {
        this.bestLineupError = error.message;
        this.bestLineupLoading = false;
      });
    }
  },
  components: {
    PlayerProfile
  }
}
</script>

<style scoped>
.lineup-ratings {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.date-selector {
  margin-bottom: 30px;
  text-align: center;
}

.date-selector label {
  margin-right: 10px;
  font-weight: bold;
}

.date-selector input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.loading, .error, .no-lineups {
  text-align: center;
  padding: 40px;
  margin: 20px 0;
}

.error {
  color: red;
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
}

.no-lineups {
  color: #666;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

/* 今日最佳阵容 */
.best-lineup-section {
  margin: 30px 0;
  padding: 20px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.best-lineup-section h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
  border-bottom: 2px solid #2196f3;
  padding-bottom: 10px;
}

.best-lineup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.best-lineup-header .total-rating {
  font-weight: bold;
  color: #ff9800;
  font-size: 16px;
}

.best-lineup-header .total-salary {
  font-weight: bold;
  color: #2196f3;
  font-size: 16px;
}

.no-best-lineup {
  text-align: center;
  padding: 40px;
  margin: 20px 0;
  color: #666;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.lineup-list {
  margin-top: 20px;
}

.lineup-list h3 {
  margin-bottom: 20px;
  color: #555;
}

/* 百叶窗容器 */
.shutter-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 百叶窗项 */
.shutter-item {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.shutter-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.shutter-content {
  padding: 15px 20px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.shutter-content:hover {
  background-color: #f9f9f9;
}

.shutter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 15px;
}

.shutter-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.players-count {
  color: #666;
  font-size: 14px;
}

.toggle-icon {
  font-size: 12px;
  color: #666;
  transition: transform 0.2s ease;
}

/* 阵容详情 */
.lineup-details {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  background-color: #f9f9f9;
}

.lineup-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 6px;
}

.lineup-info .username {
  font-weight: bold;
  color: #333;
}

.lineup-info .salary {
  color: #2196f3;
  font-weight: bold;
}

.lineup-info .total-score {
  color: #ff9800;
  font-weight: bold;
}

.lineup-info .created-at {
  color: #999;
}

/* 权限提示 */
.permission-warning {
  padding: 20px;
  margin-bottom: 20px;
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 6px;
}

.permission-warning p {
  margin: 0;
  color: #856404;
  font-size: 14px;
  text-align: center;
}

/* 球员部分 */
.players-section {
  margin-bottom: 25px;
}

.players-section h4 {
  margin: 0 0 15px 0;
  color: #555;
  font-size: 16px;
}

/* 统计容器 */
.stats-container {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* 球员表格 */
.players-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.players-table th {
  background-color: #f5f5f5;
  padding: 12px 15px;
  text-align: center;
  font-weight: bold;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.players-table td {
  padding: 12px 15px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}

/* 保持球员姓名左对齐 */
.players-table .player-name {
  text-align: left;
}

/* 保持头像居中 */
.players-table .player-avatar {
  text-align: center;
}

.players-table tr:hover {
  background-color: #f9f9f9;
}

/* 球员头像 */
.players-table .player-avatar {
  width: 60px;
}

.players-table .player-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #e0e0e0;
}

/* 球员姓名 */
.players-table .player-name {
  font-weight: bold;
  color: #333;
}

/* 球员槽位 */
.players-table .player-slot {
  color: #4caf50;
  font-weight: bold;
}

.players-table .score {
  font-weight: bold;
  color: #ff9800;
}

.players-table .won {
  color: #4caf50;
  font-weight: bold;
}

.players-table .lost {
  color: #f44336;
  font-weight: bold;
}

@media (max-width: 1200px) {
  .players-table {
    font-size: 12px;
  }
  
  .players-table th,
  .players-table td {
    padding: 8px 6px;
  }
}

@media (max-width: 768px) {
  .lineup-ratings {
    padding: 10px;
  }
  
  .shutter-header,
  .shutter-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .lineup-info {
    flex-direction: column;
    gap: 10px;
  }
  
  .players-table {
    font-size: 10px;
  }
  
  .players-table th,
  .players-table td {
    padding: 6px 4px;
  }
  
  .players-table .player-avatar img {
    width: 25px;
    height: 25px;
  }
}
</style>