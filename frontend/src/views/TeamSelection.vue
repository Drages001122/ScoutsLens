<template>
  <div class="page">
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PlayerList from '../components/PlayerList.vue'
import CurrentLineup from '../components/CurrentLineup.vue'
import { canPlayerPlaySlot } from '../utils/positionMapping'

// 当前阵容数据
const startingLineup = ref([])
const benchLineup = ref([])

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
</script>

<style scoped>
.page {
  padding: 20px 10px;
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
</style>
