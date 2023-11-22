import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { Vuetify3Resolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        Components({
            resolvers: [Vuetify3Resolver()],
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
            utilities: path.resolve(__dirname, "../utilities"),
            legacy: path.resolve(__dirname, "../../regulations"),
            sharedComponents: path.resolve(
                __dirname,
                "../eregs-component-lib/src/components/shared-components"
            ),
            eregsComponentLib: path.resolve(
                __dirname,
                "../eregs-component-lib"
            ),
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
    test: {
        environment : "jsdom"
    }
});
