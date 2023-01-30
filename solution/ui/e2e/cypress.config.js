
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://localhost:8000",
    videoUploadOnPasses: false,
    defaultCommandTimeout: 10000,
    retries: 2,
    chromeWebSecurity: false
  },
})

