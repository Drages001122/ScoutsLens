// API配置文件
const API_CONFIG = {
  // 基础URL
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  
  // API endpoints
  ENDPOINTS: {
    PLAYERS: '/api/players_information'
  }
};

export default API_CONFIG;