import vue from "rollup-plugin-vue";

const plugins = [vue({ needMap: false })];

export default [
    {
        // ...
        input: "components/RelatedRules.vue",
        output: {
            format: "esm",
            file: "regulations/js/RelatedRules.js",
        },
        plugins,
    },
    {
        input: "components/CollapseButton.vue",
        output: {
            format: "esm",
            file: "regulations/js/CollapseButton.js",
        },
        plugins,
    },
    {
        input: "components/Collapsible.vue",
        output: {
            format: "esm",
            file: "regulations/js/Collapsible.js",
        },
        plugins,
    },
    {
        input: "components/SupplementaryContent.vue",
        output: {
            format: "esm",
            file: "regulations/js/SupplementaryContent.js",
        },
        plugins,
    },
    {
        input: "regulations/js/main.js",
        output: {
            file: "regulations/js/main.build.js",
            format: "iife",
        },
    },
];
