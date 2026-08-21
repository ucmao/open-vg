/**
 * Workflow node type color utility
 * Provides unified color schemes for different data types
 */

export interface TypeColorOptions {
  /** Whether connected */
  connected?: boolean
  /** Whether visible */
  visible?: boolean
  /** Whether disabled/hidden */
  disabled?: boolean
  /** Whether system injected (not highlighted but displays color) */
  isSystemInjected?: boolean
}

/**
 * Get color class name for data type
 * @param type Data type (image, video, text, string, bool, int, number, etc.)
 * @param options Options
 * @returns Tailwind CSS class name
 */
export function getTypeColorClass(type: string | undefined | null, options: TypeColorOptions = {}): string {
  const { connected = false, visible = true, disabled = false, isSystemInjected = false } = options
  
  // Normalize type name
  const normalizedType = (type || 'string').toLowerCase()
  
  // Use gray if disabled or hidden
  if (disabled || (connected && !visible && !isSystemInjected)) {
    return '!bg-gray-500 !ring-2 !ring-gray-300 !ring-opacity-50'
  }
  
  // Define type color mappings
  // Use lighter colors when unconnected, brighter colors when connected
  // Medium brightness for system injected
  const typeColors: Record<string, { unconnected: string; connected: string; systemInjected: string }> = {
    // Image type - Purple
    image: {
      unconnected: '!bg-purple-400 hover:!bg-purple-500',
      connected: '!bg-purple-500 !ring-2 !ring-purple-300 !ring-opacity-75',
      systemInjected: '!bg-purple-400'
    },
    // Video type - Pink/Red-violet
    video: {
      unconnected: '!bg-pink-400 hover:!bg-pink-500',
      connected: '!bg-pink-500 !ring-2 !ring-pink-300 !ring-opacity-75',
      systemInjected: '!bg-pink-400'
    },
    // Text type - Emerald green
    text: {
      unconnected: '!bg-emerald-400 hover:!bg-emerald-500',
      connected: '!bg-emerald-500 !ring-2 !ring-emerald-300 !ring-opacity-75',
      systemInjected: '!bg-emerald-400'
    },
    // String type - Indigo
    string: {
      unconnected: '!bg-indigo-400 hover:!bg-indigo-500',
      connected: '!bg-indigo-500 !ring-2 !ring-indigo-300 !ring-opacity-75',
      systemInjected: '!bg-indigo-400'
    },
    // Alias: str
    str: {
      unconnected: '!bg-indigo-400 hover:!bg-indigo-500',
      connected: '!bg-indigo-500 !ring-2 !ring-indigo-300 !ring-opacity-75',
      systemInjected: '!bg-indigo-400'
    },
    // Integer type - Sky blue
    int: {
      unconnected: '!bg-sky-400 hover:!bg-sky-500',
      connected: '!bg-sky-500 !ring-2 !ring-sky-300 !ring-opacity-75',
      systemInjected: '!bg-sky-400'
    },
    integer: {
      unconnected: '!bg-sky-400 hover:!bg-sky-500',
      connected: '!bg-sky-500 !ring-2 !ring-sky-300 !ring-opacity-75',
      systemInjected: '!bg-sky-400'
    },
    // Aliases: i32/i64
    i32: {
      unconnected: '!bg-sky-400 hover:!bg-sky-500',
      connected: '!bg-sky-500 !ring-2 !ring-sky-300 !ring-opacity-75',
      systemInjected: '!bg-sky-400'
    },
    i64: {
      unconnected: '!bg-sky-400 hover:!bg-sky-500',
      connected: '!bg-sky-500 !ring-2 !ring-sky-300 !ring-opacity-75',
      systemInjected: '!bg-sky-400'
    },
    // Number/float type - Cyan blue
    number: {
      unconnected: '!bg-cyan-400 hover:!bg-cyan-500',
      connected: '!bg-cyan-500 !ring-2 !ring-cyan-300 !ring-opacity-75',
      systemInjected: '!bg-cyan-400'
    },
    float: {
      unconnected: '!bg-cyan-400 hover:!bg-cyan-500',
      connected: '!bg-cyan-500 !ring-2 !ring-cyan-300 !ring-opacity-75',
      systemInjected: '!bg-cyan-400'
    },
    // Boolean type - Orange
    bool: {
      unconnected: '!bg-orange-400 hover:!bg-orange-500',
      connected: '!bg-orange-500 !ring-2 !ring-orange-300 !ring-opacity-75',
      systemInjected: '!bg-orange-400'
    },
    boolean: {
      unconnected: '!bg-orange-400 hover:!bg-orange-500',
      connected: '!bg-orange-500 !ring-2 !ring-orange-300 !ring-opacity-75',
      systemInjected: '!bg-orange-400'
    },
    // Array type - Yellow
    array: {
      unconnected: '!bg-yellow-400 hover:!bg-yellow-500',
      connected: '!bg-yellow-500 !ring-2 !ring-yellow-300 !ring-opacity-75',
      systemInjected: '!bg-yellow-400'
    },
    // Object type - Indigo
    object: {
      unconnected: '!bg-indigo-400 hover:!bg-indigo-500',
      connected: '!bg-indigo-500 !ring-2 !ring-indigo-300 !ring-opacity-75',
      systemInjected: '!bg-indigo-400'
    }
  }
  
  // Find matching type
  const colorScheme = typeColors[normalizedType]
  
  if (colorScheme) {
    if (isSystemInjected) {
      return colorScheme.systemInjected
    }
    return connected ? colorScheme.connected : colorScheme.unconnected
  }
  
  // Default color (unknown type) - Gray
  if (isSystemInjected) {
    return '!bg-gray-400'
  }
  return connected 
    ? '!bg-gray-500 !ring-2 !ring-gray-300 !ring-opacity-75'
    : '!bg-gray-400 hover:!bg-gray-500'
}

/**
 * Infer data type from parameter name
 */
export function inferTypeFromName(name: string): string {
  const nameLower = name.toLowerCase()
  
  if (nameLower.includes('image') || nameLower.includes('img')) {
    return 'image'
  }
  if (nameLower.includes('video')) {
    return 'video'
  }
  if (nameLower.includes('prompt') || nameLower === 'text') {
    return 'text'
  }
  if (nameLower.includes('seed') || nameLower.includes('steps') || 
      nameLower.includes('width') || nameLower.includes('height') ||
      nameLower.includes('num') || nameLower.includes('count')) {
    return 'int'
  }
  if (nameLower.includes('scale') || nameLower.includes('strength') ||
      nameLower.includes('ratio') || nameLower.includes('weight')) {
    return 'float'
  }
  if (nameLower.includes('enable') || nameLower.includes('disable') ||
      nameLower.includes('is_') || nameLower.includes('use_')) {
    return 'bool'
  }
  
  return 'string' // Default string type
}
