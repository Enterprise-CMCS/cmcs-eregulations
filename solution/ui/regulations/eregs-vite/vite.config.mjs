import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vuetify from "vite-plugin-vuetify";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue(), vuetify({ autoImport: true })],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src"),
            composables: path.resolve(__dirname, "../composables"),
            directives: path.resolve(__dirname, "../directives"),
            eregsComponentLib: path.resolve(
                __dirname,
                "../eregs-component-lib"
            ),
            legacy: path.resolve(__dirname, "../../regulations"),
            sharedComponents: path.resolve(
                __dirname,
                "../eregs-component-lib/src/components/shared-components"
            ),
            utilities: path.resolve(__dirname, "../utilities"),
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
    test: {
        environment: "jsdom",
    },
});
