module.exports = {
    preset: "@vue/cli-plugin-unit-jest",
    testMatch: ["**/__tests__/*.js?(x)", "**/?(*.)+(spec|test).js|ts"],
    setupFiles: ["./test-setup.js"],
};
