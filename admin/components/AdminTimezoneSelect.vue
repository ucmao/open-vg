<template>
  <div class="inline-flex items-center gap-1.5 text-xs">
    <Globe class="w-3.5 h-3.5 text-gray-400 shrink-0" />
    <select
      :value="timezone"
      @change="onChange"
      class="bg-white border border-gray-300 rounded px-2 py-1 text-xs text-gray-700 outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer shadow-sm"
    >
      <option
        v-for="opt in timezoneOptions"
        :key="opt.value"
        :value="opt.value"
      >
        {{ isZh ? opt.labelZh : opt.labelEn }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Globe } from '@lucide/vue'
import { useAdminTimezone } from '~/composables/useAdminTimezone'
import { useAdminI18n } from '~/composables/useAdminI18n'

const { timezone, timezoneOptions, setTimezone } = useAdminTimezone()
const { lang } = useAdminI18n()

const isZh = computed(() => lang.value === 'zh')

const onChange = (e: Event) => {
  const target = e.target as HTMLSelectElement
  if (target && target.value) {
    setTimezone(target.value)
  }
}
</script>
