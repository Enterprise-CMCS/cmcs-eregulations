import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import aliases from "./alias.js";

export default defineConfig({
    plugins: [vue()],
    test: {
        globals: true,
        setupFiles: ["./test/configuration/setup-test.js"],
        coverage: {
            reporter: ["text", "json", "html"],
            provider: "v8",
            exclude: ["msw/**"],
        },
    },
    resolve: {
        alias: aliases,
    },
});
