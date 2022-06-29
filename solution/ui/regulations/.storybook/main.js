module.exports = {
    stories: [
        "../stories/**/*.stories.mdx",
        "../stories/**/*.stories.@(js|jsx|ts|tsx)",
        "../eregs-vite/**/*.stories.@(js|jsx|ts|tsx)",
        {
            directory: "../../prototype",
            titlePrefix: "Prototype",
            files: "**/*.stories.*"
        },
    ],
    addons: ["@storybook/addon-links", "@storybook/addon-essentials", "@storybook/preset-scss"],
    core: {
        builder: "webpack5",
    },
    staticDirs: [
        { from: "../../../static-assets/regulations/images", to: "images" },
        { from: "../../../static-assets/regulations/fonts", to: "fonts" },
    ],
};
