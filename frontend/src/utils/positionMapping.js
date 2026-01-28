export const getAvailableSlots = (position) => {
  const slotMapping = {
    'Guard': ['PG', 'SG'],
    'Forward': ['SF', 'PF'],
    'Center': ['C'],
    'Guard-Forward': ['SG', 'SF'],
    'Forward-Center': ['PF', 'C'],
    'Center-Forward': ['PF', 'C'],
    'Forward-Guard': ['SG', 'SF']
  }

  return slotMapping[position] || []
}

export const canPlayerPlaySlot = (position, slot) => {
  const availableSlots = getAvailableSlots(position)
  return availableSlots.includes(slot)
}

export const slotNames = {
  'PG': '控球后卫',
  'SG': '得分后卫',
  'SF': '小前锋',
  'PF': '大前锋',
  'C': '中锋'
}

export const slotOrder = ['PG', 'SG', 'SF', 'PF', 'C']
