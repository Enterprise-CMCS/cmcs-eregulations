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
        input: "components/SupplementalContent.vue",
        output: {
            format: "esm",
            file: "regulations/js/SupplementalContent.js",
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
        input: "components/TableComponent.vue",
        output: {
            format: "esm",
            file: "regulations/js/TableComponent.js",
        },
        plugins,
    },
    {
        input: "components/ResourceContent.vue",
        output: {
            format: "esm",
            file: "regulations/js/ResourceContent.js",
        },
        plugins,
    },
    {
        input: "regulations/js/main.js",
        output: {
            file: "regulations/js/main.build.js",
            format: "iife",
        },
        plugins,
    },
];
