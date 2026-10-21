const { defineConfig } = require("cypress");

module.exports = defineConfig({
    expose: {
        TEST_ENV: process.env.CYPRESS_TEST_ENV || process.env.TEST_ENV || "",
        ADMIN_LOGIN_TOKEN_REQUIRED: process.env.CYPRESS_ADMIN_LOGIN_TOKEN_REQUIRED || "true",
    },
    e2e: {
        baseUrl: "http://localhost:8000",
        defaultCommandTimeout: 10000,
        retries: 2,
        chromeWebSecurity: false,
        setupNodeEvents(on, config) {
            return require("./cypress/plugins/index.js")(on, config);
        },
    },
});
