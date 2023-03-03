const path = require("path");

module.exports = {
    stories: [
        "../stories/**/*.stories.mdx",
        "../stories/**/*.stories.@(js|jsx|ts|tsx)",
        "../eregs-vite/**/*.stories.@(js|jsx|ts|tsx)",
        {
            directory: "../../prototype",
            titlePrefix: "Prototype",
            files: "**/*.stories.*",
        },
    ],
    addons: [
        "@storybook/addon-links",
        "@storybook/addon-essentials",
        "@storybook/preset-scss",
    ],
    core: {
        builder: "webpack5",
    },
    staticDirs: [
        "../msw",
        { from: "../../../static-assets/regulations/images", to: "images" },
        { from: "../../../static-assets/regulations/fonts", to: "fonts" },
    ],
    webpackFinal: async (config) => {
        config.resolve.alias = {
            vue: "vue/dist/vue.js",
            legacy: path.resolve(__dirname, "../../regulations"),
            "legacy-static": path.resolve(
                __dirname,
                "../../../static-assets/regulations"
            ),
            mocks: "../msw/mocks",
            // handle vue-cli specific @ notation for prototype
            "@": path.resolve(__dirname, "../../prototype/src"),
        };

        config.module.rules.push({
            test: /\.m?js/,
            resolve: {
                fullySpecified: false,
            },
        });

        return config;
    },
};
