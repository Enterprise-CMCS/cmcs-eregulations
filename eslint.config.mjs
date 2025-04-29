// eslint.config.mjs
import { defineConfig } from "eslint/config";
import globals from "globals";
import pluginCypress from "eslint-plugin-cypress/flat";
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";

export default defineConfig([
    { files: ["**/*.{js,mjs,cjs,ts}"] },
    { ignores: ["**/node_modules/*", "**/dist/*", "**/static-assets/*"] },
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
            },
        },
    },
    pluginJs.configs.recommended,
    {
        files: [
            "cdk-eregs/**/*.js",
            "cdk-eregs/**/*.mjs",
            "cdk-eregs/**/*.cjs",
            "cdk-eregs/**/*.ts"
        ],
        plugins: {
            typescript: tseslint,
        },
        extends: [
            tseslint.configs.recommended,
        ],
    },
    {
        files: ["./solution/ui/e2e/**/*.js"],
        plugins: {
            cypress: pluginCypress,
        },
        extends: [
            pluginCypress.configs.recommended,
        ],
        rules: {
            "cypress/no-unnecessary-waiting": "off"
        },
    },
    {
        files: [
            "./solution/ui/regulations/**/*.js",
            "./solution/ui/regulations/**/*.mjs",
            "./solution/ui/regulations/**/*.cjs",
            "./solution/ui/regulations/**/*.ts",
            "./solution/ui/regulations/**/*.vue"
        ],
        plugins: {
            vue: pluginVue,
        },
        extends: [
            ...pluginVue.configs["flat/recommended"],
        ],
        rules: {
            "vue/order-in-components": "off",
            "vue/max-attributes-per-line": [
                "error",
                {
                    singleline: {
                        max: 2,
                    },
                    multiline: {
                        max: 1,
                    },
                },
            ],
            "vue/multi-word-component-names": "off",
            "vue/no-multiple-template-root": "off",
            "vue/no-v-html": "off",
            "vue/html-indent": [
                "error",
                4,
                {
                    attribute: 1,
                    baseIndent: 1,
                    closeBracket: 0,
                    alignAttributesVertically: false,
                    ignores: [],
                },
            ],
        },
    },
    {
        rules: {
            indent: ["error", 4, { SwitchCase: 1 }],
            eqeqeq: "off",
            "import/no-unresolved": "off",
            "import/first": "off",
            "no-console": ["error", { allow: ["warn", "error", "info", "table"] }],
            "no-nested-ternary": "off",
            "prefer-template": "off",
            "no-unused-vars": [
                "error", {
                    argsIgnorePattern: "^_",
                    varsIgnorePattern: "^_",
                    caughtErrorsIgnorePattern: "^_",
                }
            ],
        },
    },
]);
