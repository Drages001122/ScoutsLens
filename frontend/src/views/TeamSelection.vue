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

// 当前阵容数据
const startingLineup = ref([])
const benchLineup = ref([])

// 将球员添加到替补阵容
const addPlayerToBench = (player) => {
  // 添加到替补阵容
  benchLineup.value.push(player)
}

// 将球员从替补阵容移动到首发阵容
const moveToStartingLineup = (player) => {
  // 从替补阵容中移除
  benchLineup.value = benchLineup.value.filter(p => p.id !== player.id)
  // 添加到首发阵容
  startingLineup.value.push(player)
}

// 将球员从首发阵容移动到替补阵容
const moveToBench = (player) => {
  // 从首发阵容中移除
  startingLineup.value = startingLineup.value.filter(p => p.id !== player.id)
  // 添加到替补阵容
  benchLineup.value.push(player)
}

// 将球员从替补阵容移出阵容
const removeFromLineup = (player) => {
  // 从替补阵容中移除
  benchLineup.value = benchLineup.value.filter(p => p.id !== player.id)
}
</script>

<style scoped>
.page {
  padding: 20px;
}

.content-container {
  display: flex;
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>