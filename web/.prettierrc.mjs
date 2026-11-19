export default {
  // prettier-plugin-tailwindcss must be last; it sorts class lists using the
  // tokens in app.css.
  plugins: [
    'prettier-plugin-ember-template-tag',
    'prettier-plugin-tailwindcss',
  ],
  tailwindStylesheet: './app/styles/app.css',
  overrides: [
    {
      files: '*.{js,gjs,ts,gts,mjs,mts,cjs,cts}',
      options: {
        singleQuote: true,
        templateSingleQuote: false,
      },
    },
  ],
};
