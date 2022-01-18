import vue from "rollup-plugin-vue";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import alias from "@rollup/plugin-alias";
import commonjs from "@rollup/plugin-commonjs";

const plugins = [
    nodeResolve(),
    commonjs(),
    vue({ needMap: false }),
    alias({
        entries: [
            { find: "vue", replacement: "../../node_modules/vue" },
        ],
    }),
];

export default [
    {
        // ...
        input: "components/RelatedRules.vue",
        output: {
            format: "esm",
            file: "js/RelatedRules.js",
        },
        plugins,
    },
    {
        input: "components/CollapseButton.vue",
        output: {
            format: "esm",
            file: "js/CollapseButton.js",
        },
        plugins,
    },
    {
        input: "components/Collapsible.vue",
        output: {
            format: "esm",
            file: "js/Collapsible.js",
        },
        plugins,
    },
    {
        input: "components/SupplementalContent.vue",
        output: {
            format: "esm",
            file: "js/SupplementalContent.js",
        },
        plugins,
    },
    {
        input: "components/tooltips/CopyBtn.vue",
        output: {
            format: "esm",
            file: "js/CopyBtn.js",
        },
        plugins,
    },
    {
        input: "components/TableComponent.vue",
        output: {
            format: "esm",
            file: "js/TableComponent.js",
        },
        plugins,
    },
    {
        input: "js/main.js",
        output: {
            file: "../../backend/regulations/static/js/main.build.js",
            format: "iife",
        },
        plugins,
    },
];
