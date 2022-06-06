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
    managerHead: (head, { configType }) => {
        if (configType === "PRODUCTION") {
            return `
                ${head}
                <base href="/${process.env.STORYBOOK_BASE}/">
              `;
        }
    },
    staticDirs: [
        { from: "../../../static-assets/regulations/images", to: "images" },
        { from: "../../../static-assets/regulations/fonts", to: "fonts" },
    ],
};
