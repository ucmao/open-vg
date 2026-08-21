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
    'vue/no-use-v-if-with-v-for': 'off',
    'vue/no-multiple-template-root': 'off',
    'vue/valid-v-on': 'off',
    'vue/no-unused-vars': 'off',
    'no-cond-assign': 'off',
    'no-empty': 'off',
    'no-constant-condition': 'off',
    'no-irregular-whitespace': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }]
  }
}
