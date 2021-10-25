import vue from "rollup-plugin-vue";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";

const plugins = [nodeResolve(), commonjs(), vue({ needMap: false })];

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
        input: "components/tooltips/CopyBtn.vue",
        output: {
            format: "esm",
            file: "regulations/js/CopyBtn.js",
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
