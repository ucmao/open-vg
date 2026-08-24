import { createConfigForNuxt } from '@nuxt/eslint-config'

export default createConfigForNuxt().append({
  rules: {
    'vue/multi-word-component-names': 'off',
    'no-undef': 'off',
    'vue/max-attributes-per-line': 'off',
    'vue/singleline-html-element-content-newline': 'off',
    'vue/multiline-html-element-content-newline': 'off',
    'vue/html-self-closing': 'off',
    'vue/attributes-order': 'off',
    'vue/html-indent': 'off',
    'vue/no-v-html': 'off',
    'vue/prop-name-casing': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-dynamic-delete': 'off',
    '@typescript-eslint/unified-signatures': 'off',
    'import/first': 'off',
    'nuxt/prefer-import-meta': 'off',
    'vue/no-multiple-template-root': 'off',
  },
})
