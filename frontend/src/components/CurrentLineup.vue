<template>
  <div class="current-lineup-container">
    <!-- 薪资信息 -->
    <div class="salary-info">
      <div class="salary-info-item">
        <span class="salary-info-label">已选球员数量</span>
        <span class="salary-info-value">{{ selectedPlayerCount }}</span>
      </div>
      <div class="salary-info-item">
        <span class="salary-info-label">已选薪资</span>
        <span class="salary-info-value">${{ selectedSalary.toLocaleString() }}</span>
      </div>
      <div class="salary-info-item">
        <span class="salary-info-label">剩余可支配薪资</span>
        <span class="salary-info-value" :class="{ 'negative': remainingSalary < 0 }">${{ remainingSalary.toLocaleString() }}</span>
      </div>
    </div>

    <!-- 首发阵容 - 5个固定槽位 -->
    <div class="lineup-section">
      <h4>首发阵容</h4>
      <div class="starting-slots">
        <div 
          v-for="slot in slotOrder" 
          :key="slot" 
          class="slot-card"
          :class="{ 'empty': !startingSlots[slot] }"
        >
          <div class="slot-header">
            <span class="slot-name">{{ slotNames[slot] }}</span>
            <span class="slot-code">{{ slot }}</span>
          </div>
          <div v-if="startingSlots[slot]" class="slot-player">
            <img 
              :src="`/player_avatars/${startingSlots[slot].player_id}.png`" 
              :alt="startingSlots[slot].full_name" 
              class="player-avatar"
              onerror="this.src='https://via.placeholder.com/60'"
            >
            <div class="player-info">
              <div class="player-name">{{ startingSlots[slot].full_name }}</div>
              <div class="player-team">{{ translateTeam(startingSlots[slot].team_name) }}</div>
              <div class="player-position">{{ translatePosition(startingSlots[slot].position) }}</div>
              <div class="player-salary">${{ startingSlots[slot].salary.toLocaleString() }}</div>
            </div>
            <button class="action-btn bench-btn" @click="moveToBench(startingSlots[slot])">加入替补</button>
          </div>
          <div v-else class="slot-empty">
            <span class="empty-text">空缺</span>
          </div>
        </div>
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
            <th>球队</th>
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
            <td class="player-team-cell">{{ translateTeam(player.team_name) }}</td>
            <td class="player-position-cell">{{ translatePosition(player.position) }}</td>
            <td class="player-salary-cell">${{ player.salary.toLocaleString() }}</td>
            <td class="player-action-cell">
              <button class="action-btn start-btn" @click="showSlotSelection(player)">加入首发</button>
              <button class="action-btn remove-btn" @click="removeFromLineup(player)">移出阵容</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="no-data" v-else>
        暂无替补球员
      </div>
    </div>

    <!-- 槽位选择模态框 -->
    <div v-if="showSlotModal" class="modal-overlay" @click="closeSlotModal">
      <div class="modal-content" @click.stop>
        <h3>选择首发位置</h3>
        <p class="player-info-text">{{ selectedPlayer?.full_name }} ({{ translateTeam(selectedPlayer?.team_name) }})</p>
        <p class="player-info-text">{{ translatePosition(selectedPlayer?.position) }}</p>
        <div class="slot-options">
          <button 
            v-for="slot in availableSlots" 
            :key="slot"
            class="slot-option-btn"
            @click="selectSlot(slot)"
          >
            {{ slotNames[slot] }} ({{ slot }})
          </button>
        </div>
        <button class="modal-close-btn" @click="closeSlotModal">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { translatePosition, translateTeam } from '../utils/translation'
import { getAvailableSlots, slotNames, slotOrder } from '../utils/positionMapping'

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

// 状态
const salaryCap = ref(187895000)
const showSlotModal = ref(false)
const selectedPlayer = ref(null)
const availableSlots = ref([])

// 计算属性
const selectedPlayerCount = computed(() => {
  return props.startingLineup.length + props.benchLineup.length
})

const selectedSalary = computed(() => {
  const startingSalary = props.startingLineup.reduce((sum, player) => sum + player.salary, 0)
  const benchSalary = props.benchLineup.reduce((sum, player) => sum + player.salary, 0)
  return startingSalary + benchSalary
})

const remainingSalary = computed(() => {
  return salaryCap.value - selectedSalary.value
})

// 将首发阵容转换为槽位对象
const startingSlots = computed(() => {
  const slots = {}
  slotOrder.forEach(slot => {
    slots[slot] = null
  })
  
  props.startingLineup.forEach(player => {
    if (player.slot) {
      slots[player.slot] = player
    }
  })
  
  return slots
})

// 获取薪资上限
const fetchSalaryCap = async () => {
  try {
    const response = await fetch('/api/rule/salary_cap')
    if (response.ok) {
      const data = await response.json()
      salaryCap.value = data.salary_cap
    }
  } catch (error) {
    console.error('获取薪资上限失败:', error)
  }
}

onMounted(() => {
  fetchSalaryCap()
})

// 将球员从首发阵容移动到替补阵容
const moveToBench = (player) => {
  emit('move-to-bench', player)
}

// 显示槽位选择模态框
const showSlotSelection = (player) => {
  selectedPlayer.value = player
  availableSlots.value = getAvailableSlots(player.position)
  showSlotModal.value = true
}

// 关闭槽位选择模态框
const closeSlotModal = () => {
  showSlotModal.value = false
  selectedPlayer.value = null
  availableSlots.value = []
}

// 选择槽位
const selectSlot = (slot) => {
  if (selectedPlayer.value) {
    emit('move-to-starting', selectedPlayer.value, slot)
    closeSlotModal()
  }
}

// 将球员从替补阵容移出阵容
const removeFromLineup = (player) => {
  emit('remove-from-lineup', player)
}
</script>

<style scoped>
.current-lineup-container {
  flex: 1;
  min-width: 0;
}

.salary-info {
  display: flex;
  justify-content: space-between;
  background-color: #e3f2fd;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.salary-info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.salary-info-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.salary-info-value {
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
}

.salary-info-value.negative {
  color: #f44336;
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

.starting-slots {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  width: 100%;
}

.slot-card {
  flex: 1;
  min-width: calc(20% - 8px);
  max-width: none;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.slot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.slot-card.empty {
  background-color: #f5f5f5;
}

.slot-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slot-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.slot-code {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255,255,255,0.8);
  background-color: rgba(0,0,0,0.2);
  padding: 2px 6px;
  border-radius: 4px;
}

.slot-player {
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.player-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #f0f0f0;
  border: 3px solid #667eea;
}

.slot-player .player-info {
  text-align: center;
  width: 100%;
}

.slot-player .player-name {
  font-weight: 600;
  color: #333;
  font-size: 14px;
  margin-bottom: 4px;
}

.slot-player .player-team {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.slot-player .player-position {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.slot-player .player-salary {
  font-weight: 500;
  color: #4caf50;
  font-size: 13px;
}

.slot-empty {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-text {
  font-size: 14px;
  color: #999;
  font-style: italic;
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

.player-team-cell {
  color: #666;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}

.player-info-text {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.slot-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.slot-option-btn {
  padding: 12px 20px;
  background-color: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.2s;
}

.slot-option-btn:hover {
  background-color: #667eea;
  border-color: #667eea;
  color: white;
  transform: translateX(5px);
}

.modal-close-btn {
  width: 100%;
  padding: 10px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.modal-close-btn:hover {
  background-color: #da190b;
}
</style>
