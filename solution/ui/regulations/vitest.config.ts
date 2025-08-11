import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";
import aliases from "./alias.js";

export default defineConfig({
    plugins: [vue()],
    test: {
        server: {
            deps: {
                inline: ["vuetify"],
            },
        },
        globals: true,
        setupFiles: ["./test/configuration/setup-test.js"],
        environment: "jsdom",
        environmentOptions: {
            jsdom: {
                url: "http://mock-url.com",
            },
        },
        coverage: {
            reporter: ["text", "json", "html"],
            provider: "v8",
            include: [
                "**/composables/**/*",
                "**/directives/**/*",
                "**/eregs-component-lib/src/**/*",
                "**/eregs-vite/src/components/**/*",
                "!**/eregs-vite/src/components/svgs/**/*",
                "**/eregs-vite/src/views/**/*",
                "**/test/**/*",
                "**/utilities/**/*",
            ],
            reportOnFailure: true,
        },
    },
    resolve: {
        alias: aliases,
    },
});
