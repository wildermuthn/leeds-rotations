module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: [
    'plugin:react/recommended'
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    },
    ecmaVersion: 12,
    sourceType: 'module'
  },
  plugins: [
    'react'
  ],
  rules: {
    'react/prop-types': 'off',
    'react/no-unescaped-entities': 'off',
    'no-unused-vars': 'warn',
    'no-debugger': 'warn',
    'no-else-return': 'warn',
    'object-curly-spacing': ['warn', 'always'],
    'space-before-blocks': ['warn', 'always'],
    'brace-style': ['warn', '1tbs'],
    semi: ['warn', 'never'],
    indent: [
      'warn',
      2,
      { SwitchCase: 1 }
    ]
  }
}
