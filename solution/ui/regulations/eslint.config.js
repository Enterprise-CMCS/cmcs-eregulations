// eslint.config.js
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import globals from "globals";
import globalConfig from "../../../eslint-global-rules.mjs";

export default [
    {
        ignores: ["**/dist/"],
    },
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
            },
        },
    },
    pluginJs.configs.recommended,
    ...pluginVue.configs["flat/recommended"],
    {
        rules: {
            ...globalConfig,
            indent: ["error", 4, { SwitchCase: 1 }],
            "no-unused-vars": [
                "error", {
                    argsIgnorePattern: "^_",
                    varsIgnorePattern: "^_",
                    caughtErrorsIgnorePattern: "^_",
                }
            ],
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
];
