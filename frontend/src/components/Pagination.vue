<template>
  <div class="pagination" v-if="showPagination">
    <div class="per-page-selector" v-if="showPerPageSelector">
      <label>每页数量：</label>
      <select 
        v-model="internalPerPage" 
        @change="handlePerPageChange"
        class="per-page-select"
      >
        <option 
          v-for="option in perPageOptions" 
          :key="option" 
          :value="option"
        >
          {{ option }}
        </option>
      </select>
    </div>
    
    <div class="page-controls">
      <button 
        class="pagination-btn" 
        @click="goToFirstPage" 
        :disabled="currentPage === 1"
        :class="{ disabled: currentPage === 1 }"
      >
        首页
      </button>
      <button 
        class="pagination-btn" 
        @click="goToPreviousPage" 
        :disabled="currentPage === 1"
        :class="{ disabled: currentPage === 1 }"
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
        :class="{ disabled: currentPage === totalPages }"
      >
        下一页
      </button>
      <button 
        class="pagination-btn" 
        @click="goToLastPage" 
        :disabled="currentPage === totalPages"
        :class="{ disabled: currentPage === totalPages }"
      >
        末页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
    default: 1
  },
  totalPages: {
    type: Number,
    required: true,
    default: 1
  },
  totalItems: {
    type: Number,
    required: true,
    default: 0
  },
  perPage: {
    type: Number,
    default: 10
  },
  showPerPageSelector: {
    type: Boolean,
    default: true
  },
  perPageOptions: {
    type: Array,
    default: () => [10, 15, 20, 25, 50]
  }
})

const emit = defineEmits(['page-change', 'per-page-change'])

const internalPerPage = ref(props.perPage)

const showPagination = computed(() => {
  return props.totalPages > 0 && props.totalItems > 0
})

watch(() => props.perPage, (newVal) => {
  internalPerPage.value = newVal
})

const goToPage = (page) => {
  if (page < 1 || page > props.totalPages) return
  emit('page-change', page)
}

const goToFirstPage = () => {
  goToPage(1)
}

const goToLastPage = () => {
  goToPage(props.totalPages)
}

const goToPreviousPage = () => {
  if (props.currentPage > 1) {
    goToPage(props.currentPage - 1)
  }
}

const goToNextPage = () => {
  if (props.currentPage < props.totalPages) {
    goToPage(props.currentPage + 1)
  }
}

const handlePerPageChange = () => {
  emit('per-page-change', internalPerPage.value)
}
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  flex-wrap: wrap;
  gap: 15px;
}

.per-page-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.per-page-selector label {
  font-size: 14px;
  color: #333;
}

.per-page-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.per-page-select:hover {
  border-color: #999;
}

.per-page-select:focus {
  outline: none;
  border-color: #4a90e2;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  padding: 6px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(.disabled) {
  background-color: #f5f5f5;
  border-color: #999;
}

.pagination-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f9f9f9;
}

.page-info {
  padding: 0 12px;
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    align-items: center;
  }
  
  .page-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
