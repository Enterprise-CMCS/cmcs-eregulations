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
            "@": path.resolve(__dirname, "src"),
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
        environment : "jsdom"
    }
});
