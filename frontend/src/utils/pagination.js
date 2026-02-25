export class PaginationError extends Error {
  constructor(message) {
    super(message)
    this.name = 'PaginationError'
  }
}

export class InvalidPageError extends PaginationError {
  constructor(message) {
    super(message)
    this.name = 'InvalidPageError'
  }
}

export class InvalidPerPageError extends PaginationError {
  constructor(message) {
    super(message)
    this.name = 'InvalidPerPageError'
  }
}

export function paginate(items, page, perPage, options = {}) {
  const {
    itemsKey = 'items',
    maxPerPage = null
  } = options

  if (page < 1) {
    throw new InvalidPageError(`页码必须大于等于1，当前值: ${page}`)
  }

  if (perPage < 1) {
    throw new InvalidPerPageError(`每页数量必须大于等于1，当前值: ${perPage}`)
  }

  if (maxPerPage !== null && perPage > maxPerPage) {
    throw new InvalidPerPageError(`每页数量不能超过${maxPerPage}，当前值: ${perPage}`)
  }

  const totalItems = items.length
  const totalPages = perPage > 0 ? Math.ceil(totalItems / perPage) : 0

  if (page > totalPages && totalPages > 0) {
    throw new InvalidPageError(`页码超出范围，最大页码为${totalPages}，当前值: ${page}`)
  }

  const startIdx = (page - 1) * perPage
  const endIdx = startIdx + perPage
  const paginatedItems = items.slice(startIdx, endIdx)

  return {
    [itemsKey]: paginatedItems,
    pagination: {
      current_page: page,
      per_page: perPage,
      total_items: totalItems,
      total_pages: totalPages
    }
  }
}

export function getPaginationInfo(totalItems, page, perPage) {
  const totalPages = perPage > 0 ? Math.ceil(totalItems / perPage) : 0

  return {
    current_page: page,
    per_page: perPage,
    total_items: totalItems,
    total_pages: totalPages,
    has_next: page < totalPages,
    has_previous: page > 1
  }
}

export function calculateOffset(page, perPage) {
  return (page - 1) * perPage
}

export function validatePaginationParams(page, perPage, maxPerPage = null) {
  if (page < 1) {
    throw new InvalidPageError(`页码必须大于等于1，当前值: ${page}`)
  }

  if (perPage < 1) {
    throw new InvalidPerPageError(`每页数量必须大于等于1，当前值: ${perPage}`)
  }

  if (maxPerPage !== null && perPage > maxPerPage) {
    throw new InvalidPerPageError(`每页数量不能超过${maxPerPage}，当前值: ${perPage}`)
  }
}

export function buildPaginationQueryParams(page, perPage, additionalParams = {}) {
  const params = new URLSearchParams()
  params.append('page', page)
  params.append('per_page', perPage)

  Object.keys(additionalParams).forEach(key => {
    const value = additionalParams[key]
    if (Array.isArray(value)) {
      value.forEach(item => params.append(key, item))
    } else if (value !== undefined && value !== null) {
      params.append(key, value)
    }
  })

  return params
}

export function extractPaginationFromResponse(response) {
  return {
    items: response.items || response.players || [],
    pagination: response.pagination || {
      current_page: 1,
      per_page: 10,
      total_items: 0,
      total_pages: 0
    }
  }
}

export function usePagination(fetchFunction, options = {}) {
  const {
    initialPage = 1,
    initialPerPage = 10,
    maxPerPage = 100
  } = options

  const currentPage = ref(initialPage)
  const perPage = ref(initialPerPage)
  const totalItems = ref(0)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const fetchData = async (...args) => {
    loading.value = true
    error.value = null

    try {
      const response = await fetchFunction(currentPage.value, perPage.value, ...args)
      
      if (response.pagination) {
        totalItems.value = response.pagination.total_items
        totalPages.value = response.pagination.total_pages
      }

      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      return fetchData()
    }
    return Promise.reject(new InvalidPageError('页码超出范围'))
  }

  const goToFirstPage = () => goToPage(1)
  const goToLastPage = () => goToPage(totalPages.value)
  const goToPreviousPage = () => {
    if (currentPage.value > 1) {
      return goToPage(currentPage.value - 1)
    }
    return Promise.resolve()
  }
  const goToNextPage = () => {
    if (currentPage.value < totalPages.value) {
      return goToPage(currentPage.value + 1)
    }
    return Promise.resolve()
  }

  const changePerPage = (newPerPage) => {
    validatePaginationParams(currentPage.value, newPerPage, maxPerPage)
    perPage.value = newPerPage
    currentPage.value = 1
    return fetchData()
  }

  const reset = () => {
    currentPage.value = initialPage
    perPage.value = initialPerPage
    totalItems.value = 0
    totalPages.value = 0
    loading.value = false
    error.value = null
  }

  return {
    currentPage,
    perPage,
    totalItems,
    totalPages,
    loading,
    error,
    fetchData,
    goToPage,
    goToFirstPage,
    goToLastPage,
    goToPreviousPage,
    goToNextPage,
    changePerPage,
    reset
  }
}
