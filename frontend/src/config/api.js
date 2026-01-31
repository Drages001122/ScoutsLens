// API配置文件
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

// 构建完整的API endpoints
const buildEndpoint = (path) => `${BASE_URL}${path}`;

const API_CONFIG = {
  // 基础URL - 使用相对路径，让nginx处理代理
  BASE_URL,

  // API endpoints
  ENDPOINTS: {
    BASIC_INFORMATION: buildEndpoint("/api/basic_information"),
    STATS: buildEndpoint("/api/stats"),
    LINEUP: {
      CREATE: buildEndpoint("/api/lineup/create"),
    },
  },
};

export default API_CONFIG;
