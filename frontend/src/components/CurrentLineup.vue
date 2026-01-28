<template>
  <div class="current-lineup-container">
    <h3>当前阵容</h3>
    
    <!-- 首发阵容 -->
    <div class="lineup-section">
      <h4>首发阵容</h4>
      <table class="lineup-table" v-if="startingLineup.length > 0">
        <thead>
          <tr>
            <th></th>
            <th>球员</th>
            <th>位置</th>
            <th>薪资</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="player in startingLineup" :key="player.id">
            <td class="player-avatar-cell">
              <img :src="`/player_avatars/${player.player_id}.png`" :alt="player.full_name" onerror="this.src='https://via.placeholder.com/60'">
            </td>
            <td class="player-name-cell">{{ player.full_name }}</td>
            <td class="player-position-cell">{{ translatePosition(player.position) }}</td>
            <td class="player-salary-cell">${{ player.salary.toLocaleString() }}</td>
            <td class="player-action-cell">
              <button class="action-btn bench-btn" @click="moveToBench(player)">加入替补</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="no-data" v-else>
        暂无首发球员
      </div>
    </div>
    
    <!-- 替补阵容 -->
    <div class="lineup-section">
      <h4>替补阵容</h4>
      <table class="lineup-table" v-if="benchLineup.length > 0">
        <thead>
          <tr>
            <th></th>
            <th>球员</th>
            <th>位置</th>
            <th>薪资</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="player in benchLineup" :key="player.id">
            <td class="player-avatar-cell">
              <img :src="`/player_avatars/${player.player_id}.png`" :alt="player.full_name" onerror="this.src='https://via.placeholder.com/60'">
            </td>
            <td class="player-name-cell">{{ player.full_name }}</td>
            <td class="player-position-cell">{{ translatePosition(player.position) }}</td>
            <td class="player-salary-cell">${{ player.salary.toLocaleString() }}</td>
            <td class="player-action-cell">
              <button class="action-btn start-btn" @click="moveToStartingLineup(player)">加入首发</button>
              <button class="action-btn remove-btn" @click="removeFromLineup(player)">移出阵容</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="no-data" v-else>
        暂无替补球员
      </div>
    </div>
  </div>
</template>

<script setup>
import { translatePosition } from '../utils/translation'

// Props
const props = defineProps({
  startingLineup: {
    type: Array,
    default: () => []
  },
  benchLineup: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['move-to-bench', 'move-to-starting', 'remove-from-lineup'])

// 将球员从首发阵容移动到替补阵容
const moveToBench = (player) => {
  emit('move-to-bench', player)
}

// 将球员从替补阵容移动到首发阵容
const moveToStartingLineup = (player) => {
  emit('move-to-starting', player)
}

// 将球员从替补阵容移出阵容
const removeFromLineup = (player) => {
  emit('remove-from-lineup', player)
}
</script>

<style scoped>
.current-lineup-container {
  width: 400px;
  min-width: 400px;
}

h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

h4 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.lineup-section {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.lineup-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.lineup-table th,
.lineup-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.lineup-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.lineup-table tr:hover {
  background-color: #f5f5f5;
}

.player-avatar-cell {
  width: 80px;
}

.player-avatar-cell img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
}

.player-name-cell {
  font-weight: 500;
  color: #333;
}

.player-position-cell {
  color: #333;
}

.player-salary-cell {
  font-weight: 500;
  color: #4caf50;
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

.start-btn {
  background-color: #2196f3;
  color: white;
}

.start-btn:hover {
  background-color: #0b7dda;
}

.bench-btn {
  background-color: #ff9800;
  color: white;
}

.bench-btn:hover {
  background-color: #e68a00;
}

.remove-btn {
  background-color: #f44336;
  color: white;
}

.remove-btn:hover {
  background-color: #da190b;
}

.no-data {
  text-align: center;
  padding: 40px;
  font-size: 16px;
  color: #666;
}
</style>