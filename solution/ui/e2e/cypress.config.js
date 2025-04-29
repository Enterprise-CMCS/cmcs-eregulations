const { defineConfig } = require('cypress')

module.exports = defineConfig({
    e2e: {
        baseUrl: "http://localhost:8000",
        defaultCommandTimeout: 10000,
        retries: 2,
        chromeWebSecurity: false,
        setupNodeEvents(on, config) {
            return require('./cypress/plugins/index.js')(on, config)
        },
    },
})
