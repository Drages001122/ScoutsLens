// 翻译工具函数
import translations from '../data/translations.json'

/**
 * 将英文队名翻译为中文
 * @param {string} teamName - 英文队名
 * @returns {string} 中文队名
 */
export const translateTeam = (teamName) => {
  return translations.teams[teamName] || teamName
}

/**
 * 将英文位置翻译为中文
 * @param {string} position - 英文位置
 * @returns {string} 中文位置
 */
export const translatePosition = (position) => {
  return translations.positions[position] || position
}
