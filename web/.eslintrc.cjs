module.exports = {
  root: true,
  extends: [
    '@nuxt/eslint-config'
  ],
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
    '@typescript-eslint/no-unused-vars': 'off'
  }
}
