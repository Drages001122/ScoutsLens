// API配置文件
const API_CONFIG = {
  // 基础URL - 使用相对路径，让nginx处理代理
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '',
  
  // API endpoints
  ENDPOINTS: {
    PLAYERS_INFORMATION: '/api/players_information',
    PLAYERS_GAME_STATS: '/api/players_information/game-stats',
    LINEUP: {
      CREATE: '/api/lineup/create',
      LIST: '/api/lineup/list',
      GET: '/api/lineup/',
      DELETE: '/api/lineup/'
    }
  }
};

export default API_CONFIG;