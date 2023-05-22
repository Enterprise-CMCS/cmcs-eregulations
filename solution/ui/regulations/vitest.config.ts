import vue from "@vitejs/plugin-vue2";
import { defineConfig } from "vite";
import { aliases } from './alias.js'

// This is for vue2.  When we make the transition to 3 this must change.

export default defineConfig({
    plugins: [vue()],
    test: {
        globals: true,
        setupFiles: ["./test/configuration/setup-test.js"]
    },
    resolve: {
        alias : aliases
    },

});
