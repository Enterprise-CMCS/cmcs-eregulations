// eslint.config.js
import pluginVue from "eslint-plugin-vue";
import globalConfig from "../../eslint-global-rules.mjs";

export default [
    ...pluginVue.configs["flat/recommended"],
    {
        rules: {
            ...globalConfig,
            "vue/html-indent": ["error", 4],
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
