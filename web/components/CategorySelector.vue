<template>
  <div class="space-y-2">
    <!-- Level 1 Category -->
    <div>
      <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
        {{ label }}
      </label>
      <select
        v-model="selectedLevel1"
        @change="onLevel1Change"
        class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        :disabled="disabled"
      >
        <option :value="null">{{ level1Placeholder || 'Select primary category' }}</option>
        <option
          v-for="cat in level1Categories"
          :key="cat.id"
          :value="cat.category_name"
        >
          {{ cat.category_name }}
        </option>
      </select>
    </div>

    <!-- Level 2 Category (only shown if level 1 is selected) -->
    <div v-if="selectedLevel1 && level2Categories.length > 0">
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ level2Label || 'Subcategory (optional)' }}
      </label>
      <select
        v-model="selectedLevel2"
        @change="onLevel2Change"
        class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
        :disabled="disabled"
      >
        <option :value="null">{{ level2Placeholder || 'Primary category only' }}</option>
        <option
          v-for="cat in level2Categories"
          :key="cat.id"
          :value="cat.category_name"
        >
          {{ cat.category_name }}
        </option>
      </select>
    </div>

    <!-- Display current selection -->
    <div v-if="displayValue" class="text-xs text-gray-500 mt-1">
      Selected: <span class="font-medium">{{ displayValue }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

interface Category {
  id: number
  category_name: string
  level: number
  parent_id: number | null
  children?: Category[]
}

interface Props {
  modelValue?: string | null
  label?: string
  level1Placeholder?: string
  level2Placeholder?: string
  level2Label?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  label: 'Category',
  level1Placeholder: 'Select primary category',
  level2Placeholder: 'Primary category only',
  level2Label: 'Subcategory (optional)',
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const api = useApi()
const categoryTree = ref<Category[]>([])
const selectedLevel1 = ref<string | null>(null)
const selectedLevel2 = ref<string | null>(null)
const isInitializing = ref(true) // Track if we're in initialization phase

// Computed properties
const level1Categories = computed(() => {
  return categoryTree.value || []
})

const level2Categories = computed(() => {
  if (!selectedLevel1.value) return []
  const level1 = categoryTree.value.find(cat => cat.category_name === selectedLevel1.value)
  return level1?.children || []
})

const displayValue = computed(() => {
  if (selectedLevel2.value) {
    return `${selectedLevel1.value} > ${selectedLevel2.value}`
  }
  return selectedLevel1.value || null
})

const finalCategory = computed(() => {
  if (selectedLevel2.value) {
    return `${selectedLevel1.value}|${selectedLevel2.value}`
  }
  return selectedLevel1.value || null
})

// Methods
const fetchCategoryTree = async () => {
  try {
    const response = await api.get('/api/category-pages/tree')
    if (response.success) {
      categoryTree.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch category tree:', error)
  }
}

const parseCategoryValue = (value: string | null) => {
  if (!value) {
    selectedLevel1.value = null
    selectedLevel2.value = null
    return
  }

  // Check if it's hierarchical format (Level1|Level2)
  if (value.includes('|')) {
    const [level1, level2] = value.split('|')
    selectedLevel1.value = level1
    selectedLevel2.value = level2 || null
  } else {
    // Single level category
    selectedLevel1.value = value
    selectedLevel2.value = null
  }
}

const onLevel1Change = () => {
  // Reset level 2 when level 1 changes
  selectedLevel2.value = null
  // User actively changed level 1, so emit update
  if (!isInitializing.value) {
    emit('update:modelValue', finalCategory.value)
  }
}

const onLevel2Change = () => {
  // User actively changed level 2, so emit update
  if (!isInitializing.value) {
    emit('update:modelValue', finalCategory.value)
  }
}

// Watch finalCategory and emit updates (only when user actively changes, not during init)
watch(finalCategory, (newValue) => {
  // Only emit if not initializing (user actively changed selection)
  if (!isInitializing.value) {
    emit('update:modelValue', newValue)
  }
})

// Watch modelValue to sync with parent
watch(() => props.modelValue, (newValue) => {
  if (newValue !== finalCategory.value) {
    parseCategoryValue(newValue)
  }
}, { immediate: true })

onMounted(async () => {
  await fetchCategoryTree()
  if (props.modelValue) {
    parseCategoryValue(props.modelValue)
  }
  // Mark initialization as complete after a short delay to ensure all watches have settled
  setTimeout(() => {
    isInitializing.value = false
  }, 100)
})
</script>
