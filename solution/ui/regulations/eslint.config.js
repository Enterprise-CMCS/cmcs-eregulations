// eslint.config.js
import pluginVue from "eslint-plugin-vue";
import eslintPluginPrettierRecommended from "eslint-plugin-prettier/recommended";

export default [
    ...pluginVue.configs["flat/recommended"],
    {
        rules: {
            eqeqeq: "off",
            "import/no-unresolved": "off",
            "import/first": "off",
            "no-console": ["error", { allow: ["warn", "error"] }],
            "no-nested-ternary": "off",
            "prefer-template": "off",
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
        },
    },
    eslintPluginPrettierRecommended,
];
