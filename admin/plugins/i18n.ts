export default defineNuxtPlugin(() => {
  const { translateText, formatDate, formatNumber, formatCurrency } = useAdminI18n()

  return {
    provide: {
      adminT: translateText,
      adminDate: formatDate,
      adminNumber: formatNumber,
      adminCurrency: formatCurrency
    }
  }
})
