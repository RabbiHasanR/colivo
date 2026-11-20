/**
 * Debugging:
 *   https://eslint.org/docs/latest/use/configure/debug
 *  ----------------------------------------------------
 *
 *   Print a file's calculated configuration
 *
 *     npx eslint --print-config path/to/file.js
 *
 *   Inspecting the config
 *
 *     npx eslint --inspect-config
 *
 */
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import globals from 'globals';
import js from '@eslint/js';
import { defineConfig, globalIgnores } from 'eslint/config';

import ts from 'typescript-eslint';

import ember from 'eslint-plugin-ember/recommended';
import WarpDrive from 'eslint-plugin-warp-drive/recommended';

import eslintConfigPrettier from 'eslint-config-prettier';
import qunit from 'eslint-plugin-qunit';
import n from 'eslint-plugin-n';
import boundaries from 'eslint-plugin-boundaries';

import babelParser from '@babel/eslint-parser/experimental-worker';

const parserOptions = {
  esm: {
    js: {
      ecmaFeatures: { modules: true },
      ecmaVersion: 'latest',
    },
    ts: {
      projectService: true,
      tsconfigRootDir: dirname(fileURLToPath(import.meta.url)),
    },
  },
};

export default defineConfig([
  globalIgnores([
    'dist/',
    'coverage/',
    '!**/.*',
    // Generated: by `msw init` and by `make api-types`.
    'public/mockServiceWorker.js',
    'app/data/types/api.generated.ts',
  ]),
  js.configs.recommended,
  ember.configs.base,
  ember.configs.gjs,
  ember.configs.gts,
  ...WarpDrive,
  eslintConfigPrettier,
  /**
   * https://eslint.org/docs/latest/use/configure/configuration-files#configuring-linter-options
   */
  {
    linterOptions: {
      reportUnusedDisableDirectives: 'error',
    },
  },
  {
    files: ['**/*.js'],
    languageOptions: {
      parser: babelParser,
    },
  },
  {
    files: ['**/*.{js,gjs}'],
    languageOptions: {
      parserOptions: parserOptions.esm.js,
      globals: {
        ...globals.browser,
      },
    },
  },
  {
    files: ['**/*.{ts,gts}'],
    languageOptions: {
      parser: ember.parser,
      parserOptions: parserOptions.esm.ts,
      globals: {
        ...globals.browser,
      },
    },
    extends: [
      ...ts.configs.recommendedTypeChecked,
      // https://github.com/ember-cli/ember-addon-blueprint/issues/119
      {
        ...ts.configs.eslintRecommended,
        files: undefined,
      },
      ember.configs.gts,
    ],
  },
  /**
   * Layers: dependencies point one way,
   * routes -> components -> services -> data -> models -> utils
   * (specs/tech-stack.md → Project conventions, ember-scaffold → Architecture).
   * components/ui never imports a feature folder; only app/data talks HTTP.
   */
  {
    files: ['app/**/*.{js,ts,gjs,gts}'],
    plugins: { boundaries },
    settings: {
      'import/resolver': {
        node: { extensions: ['.js', '.ts', '.gjs', '.gts'] },
      },
      'boundaries/elements': [
        { type: 'utils', pattern: 'app/utils/**', partialMatch: false },
        { type: 'models', pattern: 'app/models/**', partialMatch: false },
        { type: 'data', pattern: 'app/data/**', partialMatch: false },
        { type: 'services', pattern: 'app/services/**', partialMatch: false },
        { type: 'ui', pattern: 'app/components/ui/**', partialMatch: false },
        {
          type: 'components',
          pattern: 'app/components/**',
          partialMatch: false,
        },
        {
          type: 'routes',
          pattern: 'app/{routes,templates}/**',
          partialMatch: false,
        },
      ],
    },
    rules: {
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          policies: [
            {
              from: { element: { type: 'utils' } },
              allow: { to: { element: { types: ['utils'] } } },
            },
            {
              from: { element: { type: 'models' } },
              allow: { to: { element: { types: ['models', 'utils'] } } },
            },
            {
              from: { element: { type: 'data' } },
              allow: {
                to: { element: { types: ['data', 'models', 'utils'] } },
              },
            },
            {
              from: { element: { type: 'services' } },
              allow: {
                to: {
                  element: { types: ['services', 'data', 'models', 'utils'] },
                },
              },
            },
            {
              from: { element: { type: 'ui' } },
              allow: { to: { element: { types: ['ui', 'utils'] } } },
            },
            {
              from: { element: { type: 'components' } },
              allow: {
                to: {
                  element: {
                    types: ['components', 'ui', 'services', 'models', 'utils'],
                  },
                },
              },
            },
            {
              from: { element: { type: 'routes' } },
              allow: {
                to: {
                  element: {
                    types: [
                      'routes',
                      'components',
                      'ui',
                      'services',
                      'data',
                      'models',
                      'utils',
                    ],
                  },
                },
              },
            },
          ],
        },
      ],
    },
  },
  /**
   * Inside the layer folders, imports are relative: the boundaries rule above
   * resolves relative paths, not the colivo-web/* alias, so an alias import
   * would skip the layer check.
   */
  {
    files: [
      'app/{utils,models,data,services,components,routes,templates}/**/*.{js,ts,gjs,gts}',
    ],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['colivo-web/*'],
              message:
                'Use a relative import inside app/ so the layer rules (boundaries/dependencies) can check it.',
            },
          ],
        },
      ],
    },
  },
  /**
   * The root Playwright config runs in Node and sits outside web/tsconfig.json
   * (browser-only). `pnpm lint:types:e2e` type-checks it with the e2e project
   * (Node types); ESLint lints it without type-aware rules.
   */
  {
    files: ['playwright.config.ts'],
    extends: [ts.configs.disableTypeChecked],
    languageOptions: {
      parserOptions: { projectService: false },
      globals: { ...globals.node },
    },
  },
  {
    ...qunit.configs.recommended,
    files: ['tests/**/*-test.{js,gjs,ts,gts}'],
    plugins: {
      qunit,
    },
  },
  /**
   * CJS node files
   */
  {
    ...n.configs['flat/recommended-script'],
    files: ['**/*.cjs', 'config/**/*.js'],
    plugins: {
      n,
    },

    languageOptions: {
      sourceType: 'script',
      ecmaVersion: 'latest',
      globals: {
        ...globals.node,
      },
    },
  },
  /**
   * ESM node files
   */
  {
    ...n.configs['flat/recommended-module'],
    files: ['**/*.mjs'],
    plugins: {
      n,
    },

    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 'latest',
      parserOptions: parserOptions.esm.js,
      globals: {
        ...globals.node,
      },
    },
  },
]);
