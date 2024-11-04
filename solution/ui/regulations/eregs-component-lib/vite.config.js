import path from "path";
import fg from "fast-glob";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vuetify from "vite-plugin-vuetify";

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
        outDir: "../../../static-assets/regulations/bundles",
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
            composables: path.resolve(__dirname, "../composables"),
            directives: path.resolve(__dirname, "../directives"),
            sharedComponents: path.resolve(
                __dirname,
                "./src/components/shared-components"
            ),
            spaComponents: path.resolve(
                __dirname,
                "../eregs-vite/src/components"
            ),
            utilities: path.resolve(__dirname, "../utilities"),
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
        vuetify({ autoImport: true }),
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
