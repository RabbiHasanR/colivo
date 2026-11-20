export default {
  extends: ['stylelint-config-standard'],
  rules: {
    // Tailwind CSS v4 directives (app/styles/app.css).
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'theme',
          'apply',
          'layer',
          'utility',
          'variant',
          'custom-variant',
          'source',
          'reference',
          'plugin',
          'config',
        ],
      },
    ],
    // @apply takes Tailwind utility names, not standard CSS.
    'at-rule-prelude-no-invalid': [true, { ignoreAtRules: ['apply'] }],
    'import-notation': 'string',
    // Blank lines group the tokens in @theme (colours, owes, tags …).
    'custom-property-empty-line-before': null,
  },
};
