import path from "path";
import fg from "fast-glob";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue2";
import { VuetifyResolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";

// https://www.raulmelo.dev/blog/build-javascript-library-with-multiple-entry-points-using-vite-3
const config = {
    components: {
        entry: path.resolve(__dirname, "src/components/index.js"),
        name: "eregsComponents",
        formats: ["es"],
        fileName: (format) => `eregs-components.${format}.js`,
        outDir: "./dist",
    },
    main: {
        entry: path.resolve(__dirname, "src/main.js"),
        name: "eregsMain",
        formats: ["iife"],
        fileName: (format) => `eregs-main.${format}.js`,
        outDir: "../../../static-assets/regulations/js",
    },
};

const currentConfig = config[process.env.LIB_NAME];

if (currentConfig === undefined) {
    throw new Error("LIB_NAME is not defined or is not valid");
}

// https://vitejs.dev/config/
export default defineConfig({
    define: {
        "process.env": { NODE_ENV: "production" },
    },
    resolve: {
        alias: {
            plugins: path.resolve(__dirname, "src/plugins"),
        },
    },
    build: {
        lib: {
            ...currentConfig,
        },
        outDir: currentConfig.outDir,
        sourcemap: true,
        rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: ["vue"],
            output: {
                // Provide global variables to use in the UMD build
                // for externalized deps
                globals: {
                    vue: "Vue",
                },
            },
        },
    },
    plugins: [
        vue(),
        Components({
            resolvers: [VuetifyResolver()],
        }),
        cssInjectedByJsPlugin(),
        {
            name: "watch-external", // https://stackoverflow.com/questions/63373804/rollup-watch-include-directory/63548394#63548394
            async buildStart() {
                if (process.env.LIB_NAME === "main") {
                    const files = await fg(["dist/**/*"]);
                    files.forEach((file) => {
                        this.addWatchFile(file);
                    });
                }
            },
        },
    ],
});
