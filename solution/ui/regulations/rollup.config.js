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
    // All esm components will be created using a new Vite workflow --
    // Library mode to create a component library.
    // New directory using supervised vite setup, tweak to include Vue2 and Vuetify
    {
        // ...
        input: "js/src/components/RelatedRules.vue",
        output: {
            format: "esm",
            file: "dist/RelatedRules.js",
        },
        plugins,
    },
    {
        input: "js/src/components/CollapseButton.vue",
        output: {
            format: "esm",
            file: "dist/CollapseButton.js",
        },
        plugins,
    },
    {
        input: "js/src/components/Collapsible.vue",
        output: {
            format: "esm",
            file: "dist/Collapsible.js",
        },
        plugins,
    },
    {
        input: "js/src/components/SupplementalContent.vue",
        output: {
            format: "esm",
            file: "dist/SupplementalContent.js",
        },
        plugins,
    },
    {
        input: "js/src/components/tooltips/TooltipContainer.vue",
        output: {
            format: "esm",
            file: "dist/TooltipContainer.js",
        },
        plugins,
    },
    {
        input: "js/src/components/TableComponent.vue",
        output: {
            format: "esm",
            file: "dist/TableComponent.js",
        },
        plugins,
    },
    {
        input: "js/src/components/PrintBtn.vue",
        output: {
            format: "esm",
            file: "dist/PrintBtn.js",
        },
        plugins,
    },
    {
        input: "js/src/components/ViewResourcesLink.vue",
        output: {
            format: "esm",
            file: "dist/ViewResourcesLink.js",
        },
        plugins,
    },
    {
        input: "js/src/components/RecentChangesContainer.vue",
        output: {
            format: "esm",
            file: "dist/RecentChangesContainer.js",
        },
        plugins,
    },
    {
        input: "js/src/components/LastParserSuccessDate.vue",
        output: {
            format: "esm",
            file: "dist/LastParserSuccessDate.js",
        },
        plugins,
    },
    {
        input: "js/src/components/BlockingModal.vue",
        output: {
            format: "esm",
            file: "dist/BlockingModal.js",
        },
        plugins,
    },
    {
        input: "js/src/components/BlockingModalTrigger.vue",
        output: {
            format: "esm",
            file: "dist/BlockingModalTrigger.js",
        },
        plugins,
    },
    {
        input: "js/src/components/FlashBanner.vue",
        output: {
            format: "esm",
            file: "dist/FlashBanner.js",
        },
        plugins,
    },
    {
        input: "js/src/components/IFrameContainer.vue",
        output: {
            format: "esm",
            file: "dist/IFrameContainer.js",
        },
        plugins,
    },
    {
        input: "js/src/components/tooltips/CopyCitation.vue",
        output: {
            format: "esm",
            file: "dist/CopyCitation.js",
        },
        plugins,
    },
    {
        input: "js/src/components/tooltips/GovInfoLinks.vue",
        output: {
            format: "esm",
            file: "dist/GovInfoLinks.js",
        },
        plugins,
    },
    // #### HYGEN INSERTION POINT DO NOT REMOVE ####
    // Keep the IIFE here but don't use Rollup for any of the components above
    {
        input: "js/main.js",
        output: {
            file: "../../static-assets/regulations/js/main.build.js",
            format: "iife",
        },
        plugins,
    },
];
