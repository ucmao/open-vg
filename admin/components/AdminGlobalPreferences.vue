<template>
  <div ref="containerRef" class="relative">
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm transition-all cursor-pointer"
    >
      <span>{{ currentLangFlag }} {{ currentLangCode.toUpperCase() }}</span>
      <span class="text-gray-300">·</span>
      <span class="text-gray-600 font-normal">{{ timezoneBadgeLabel }}</span>
      <ChevronDown class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': isOpen }" />
    </button>

    <!-- Popover Panel -->
    <div
      v-if="isOpen"
      class="absolute right-0 top-full mt-2 w-64 p-3 bg-white border border-gray-200 rounded-xl shadow-xl z-50 space-y-3"
    >
      <!-- Section 1: Language -->
      <div>
        <div class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
          {{ isZh ? '界面语言 / Language' : 'Language / 语言' }}
        </div>
        <div class="grid grid-cols-2 gap-1.5">
          <button
            v-for="l in availableLocales"
            :key="l.code"
            type="button"
            @click="setLanguage(l.code)"
            class="flex items-center justify-center gap-1.5 px-2.5 py-1.5 text-xs rounded-md border transition-all cursor-pointer"
            :class="lang === l.code ? 'bg-blue-50 border-blue-500 text-blue-700 font-medium' : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
          >
            <span>{{ l.flag }}</span>
            <span>{{ l.label }}</span>
          </button>
        </div>
      </div>

      <div class="border-t border-gray-100"></div>

      <!-- Section 2: Timezone -->
      <div>
        <div class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
          {{ isZh ? '统计时区 / Timezone' : 'Analytics Timezone' }}
        </div>
        <div class="space-y-0.5 max-h-56 overflow-y-auto">
          <button
            v-for="opt in timezoneOptions"
            :key="opt.value"
            type="button"
            @click="setTimezone(opt.value)"
            class="w-full text-left px-2.5 py-1.5 text-xs rounded-md flex items-center justify-between transition-colors cursor-pointer"
            :class="settingValue === opt.value ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-50'"
          >
            <span>{{ isZh ? opt.labelZh : opt.labelEn }}</span>
            <Check v-if="settingValue === opt.value" class="w-3.5 h-3.5 text-blue-600" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Check } from '@lucide/vue'
import { useAdminI18n } from '~/composables/useAdminI18n'
import { useAdminTimezone } from '~/composables/useAdminTimezone'

const { lang, setLanguage, availableLocales } = useAdminI18n()
const { timezone, settingValue, timezoneOptions, setTimezone } = useAdminTimezone()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const isZh = computed(() => lang.value === 'zh')
const currentLangCode = computed(() => lang.value)
const currentLangFlag = computed(() => lang.value === 'zh' ? '🇨🇳' : '🇬🇧')

const timezoneBadgeLabel = computed(() => {
  if (settingValue.value === 'Auto') {
    return 'Auto'
  }
  if (timezone.value === 'UTC') return 'UTC'
  if (timezone.value === 'America/New_York') return 'UTC-5'
  if (timezone.value === 'America/Chicago') return 'UTC-6'
  if (timezone.value === 'America/Los_Angeles') return 'UTC-8'
  if (timezone.value === 'Europe/London') return 'UTC+0'
  if (timezone.value === 'Australia/Sydney') return 'UTC+10'
  if (timezone.value === 'Asia/Tokyo') return 'UTC+9'
  if (timezone.value === 'Asia/Shanghai') return 'UTC+8'
  return timezone.value
})

function handleClickOutside(e: MouseEvent) {
  if (isOpen.value && containerRef.value && !containerRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
