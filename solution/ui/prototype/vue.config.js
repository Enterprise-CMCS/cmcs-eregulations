const path = require("path");

module.exports = {
    transpileDependencies: ["vuetify"],
    lintOnSave: false,
    css: {
        sourceMap: true,
    },
    configureWebpack: {
        resolve: {
            alias: {
                utilities: path.resolve(__dirname, "../regulations/utilities"),
                legacy: path.resolve(__dirname, "../regulations"),
                "legacy-static": path.resolve(
                    __dirname,
                    "../../static-assets/regulations"
                ),
            },
        },
    },
};
