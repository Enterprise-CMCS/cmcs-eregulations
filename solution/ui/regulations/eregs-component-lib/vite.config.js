import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue2";

// https://vitejs.dev/config/
export default defineConfig({
    build: {
        lib: {
            entry: path.resolve(__dirname, "src/components/index.js"),
            name: "eregsComponents",
            fileName: (format) => `eregs-components.${format}.js`,
        },
        rollupOptions: {
            external: ["vue"],
            output: {
                // Provide global variables to use in the UMD build
                // Add external deps here
                globals: {
                    vue: "Vue",
                },
            },
        },
    },
    plugins: [vue()],
});
