<template>
  <div class="page">
    <div class="page-header">
      <h2>阵容选择</h2>
      <div class="header-controls">
        <div class="date-selector">
          <label for="lineup-date">比赛日期</label>
          <input 
            type="date" 
            id="lineup-date" 
            v-model="selectedDate"
            :min="minDate"
          >
        </div>
        <button 
          class="publish-btn" 
          @click="showPublishModal = true"
          :disabled="!(startingLineup.length > 0 || benchLineup.length > 0)"
        >
          发布阵容
        </button>
      </div>
    </div>
    <div class="content-container">
      <!-- 左侧球员列表 -->
      <PlayerList 
        :excludePlayers="[...startingLineup, ...benchLineup]"
        @add-player="addPlayerToBench"
      />
      
      <!-- 右侧当前阵容 -->
      <CurrentLineup 
        :startingLineup="startingLineup"
        :benchLineup="benchLineup"
        @move-to-bench="moveToBench"
        @move-to-starting="moveToStartingLineup"
        @remove-from-lineup="removeFromLineup"
      />
    </div>

    <!-- 发布阵容模态框 -->
    <div v-if="showPublishModal" class="modal-overlay" @click="closePublishModal">
      <div class="modal-content" @click.stop>
        <h3>发布阵容</h3>
        <div class="modal-form">
          <div class="form-info">
            <p>首发球员: {{ startingLineup.length }}人</p>
            <p>替补球员: {{ benchLineup.length }}人</p>
            <p>总薪资: ${{ totalSalary.toLocaleString() }}</p>
          </div>
          <div class="modal-actions">
            <button class="btn cancel-btn" @click="closePublishModal">取消</button>
            <button 
              class="btn publish-submit-btn" 
              @click="publishLineup"
            >
              发布
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 成功提示 -->
    <div v-if="showSuccessMessage" class="success-message">
      <p>{{ successMessage }}</p>
      <button class="close-btn" @click="showSuccessMessage = false">×</button>
    </div>

    <!-- 错误提示 -->
    <div v-if="showErrorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
      <button class="close-btn" @click="showErrorMessage = false">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PlayerList from '../components/PlayerList.vue'
import CurrentLineup from '../components/CurrentLineup.vue'
import { canPlayerPlaySlot } from '../utils/positionMapping'
import API_CONFIG from '../config/api.js'

// 当前阵容数据
const startingLineup = ref([])
const benchLineup = ref([])

// 发布阵容相关状态
const showPublishModal = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const minDate = ref(new Date().toISOString().split('T')[0])
const showSuccessMessage = ref(false)
const showErrorMessage = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const isPublishing = ref(false)

// 计算总薪资
const totalSalary = computed(() => {
  const startingSalary = startingLineup.value.reduce((sum, player) => sum + player.salary, 0)
  const benchSalary = benchLineup.value.reduce((sum, player) => sum + player.salary, 0)
  return startingSalary + benchSalary
})

// 将球员添加到替补阵容
const addPlayerToBench = (player) => {
  benchLineup.value.push(player)
}

// 将球员从替补阵容移动到首发阵容
const moveToStartingLineup = (player, slot) => {
  // 检查球员是否可以胜任该槽位
  if (!canPlayerPlaySlot(player.position, slot)) {
    alert(`该球员不能担任 ${slot} 位置`)
    return
  }

  // 检查该槽位是否已被占用
  const existingPlayer = startingLineup.value.find(p => p.slot === slot)
  if (existingPlayer) {
    alert(`${slot} 位置已被 ${existingPlayer.full_name} 占用`)
    return
  }

  // 从替补阵容中移除
  benchLineup.value = benchLineup.value.filter(p => p.id !== player.id)
  
  // 添加到首发阵容，并标记槽位
  const playerWithSlot = { ...player, slot }
  startingLineup.value.push(playerWithSlot)
}

// 将球员从首发阵容移动到替补阵容
const moveToBench = (player) => {
  // 从首发阵容中移除
  startingLineup.value = startingLineup.value.filter(p => p.id !== player.id)
  // 添加到替补阵容，移除槽位标记
  const playerWithoutSlot = { ...player }
  delete playerWithoutSlot.slot
  benchLineup.value.push(playerWithoutSlot)
}

// 将球员从替补阵容移出阵容
const removeFromLineup = (player) => {
  // 从替补阵容中移除
  benchLineup.value = benchLineup.value.filter(p => p.id !== player.id)
}

// 打开发布阵容模态框
const openPublishModal = () => {
  showPublishModal.value = true
}

// 关闭发布阵容模态框
const closePublishModal = () => {
  showPublishModal.value = false
}

// 发布阵容
const publishLineup = async () => {
  if (!startingLineup.value.length && !benchLineup.value.length) {
    showError('阵容至少需要一名球员')
    return
  }

  isPublishing.value = true

  try {
    // 准备阵容数据
    const lineupData = {
      date: selectedDate.value,
      starting_players: startingLineup.value.map(player => ({
        player_id: player.player_id,
        full_name: player.full_name,
        team_name: player.team_name,
        position: player.position,
        salary: player.salary,
        slot: player.slot
      })),
      bench_players: benchLineup.value.map(player => ({
        player_id: player.player_id,
        full_name: player.full_name,
        team_name: player.team_name,
        position: player.position,
        salary: player.salary
      }))
    }

    // 发送请求
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LINEUP.CREATE}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(lineupData)
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '发布阵容失败')
    }

    const data = await response.json()
    showSuccess('阵容发布成功！')
    closePublishModal()
  } catch (error) {
    showError(error.message || '发布阵容失败，请重试')
  } finally {
    isPublishing.value = false
  }
}

// 显示成功消息
const showSuccess = (message) => {
  successMessage.value = message
  showSuccessMessage.value = true
  
  // 3秒后自动关闭
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 3000)
}

// 显示错误消息
const showError = (message) => {
  errorMessage.value = message
  showErrorMessage.value = true
  
  // 3秒后自动关闭
  setTimeout(() => {
    showErrorMessage.value = false
  }, 3000)
}
</script>

<style scoped>
.page {
  padding: 20px 10px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.date-selector {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-selector label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
}

.date-selector input {
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.date-selector input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.publish-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.publish-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.content-container {
  display: flex;
  gap: 20px;
  max-width: 100%;
  margin: 0 auto;
}

.content-container > :deep(*) {
  flex: 1;
}

/* 模态框样式 */
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
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-info {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
}

.form-info p {
  margin: 5px 0;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #e0e0e0;
}

.cancel-btn:hover {
  background-color: #e9ecef;
}

.publish-submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.publish-submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.publish-submit-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 消息提示样式 */
.success-message,
.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  z-index: 1001;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.success-message p,
.error-message p {
  margin: 0;
  font-size: 14px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  color: inherit;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  opacity: 0.7;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-container {
    flex-direction: column;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
  }
  
  .date-selector {
    width: 100%;
  }
  
  .date-selector input {
    width: 100%;
    box-sizing: border-box;
  }
  
  .publish-btn {
    align-self: flex-start;
  }
}
</style>
