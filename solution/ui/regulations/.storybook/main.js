module.exports = {
    stories: [
        "../stories/**/*.stories.mdx",
        "../stories/**/*.stories.@(js|jsx|ts|tsx)",
        "../eregs-vite/src/**/*.stories.@(js|jsx|ts|tsx)",
    ],
    addons: ["@storybook/addon-links", "@storybook/addon-essentials"],
    core: {
        builder: "webpack5",
    },
    staticDirs: [
        { from: "../../../static-assets/regulations/images", to: "storybook/images" },
        { from: "../../../static-assets/regulations/fonts", to: "storybook/fonts" },
    ],
};
