import { defineConfig } from "vite";
import { createVuePlugin } from "vite-plugin-vue2";
import { VuetifyResolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";

const path = require("path");

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        createVuePlugin(),
        Components({
            resolvers: [VuetifyResolver()],
        }),
    ],
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: `@import "../css/scss/main.scss";`,
            },
        },
    },
    resolve: {
        alias: {
            legacy: path.resolve(__dirname, "../../regulations"),
            "@": path.resolve(__dirname, "src"),
        },
    },
    build: {
        outDir: "../../../static-assets/regulations/vite",
        sourcemap: true,
        rollupOptions: {
            output: {
                entryFileNames: `[name].js`,
                chunkFileNames: `[name].js`,
                assetFileNames: `[name].[ext]`,
            },
        },
    },
});
