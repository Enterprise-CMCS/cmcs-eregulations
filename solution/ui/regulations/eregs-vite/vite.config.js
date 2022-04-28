import { defineConfig } from "vite";
import { createVuePlugin } from "vite-plugin-vue2";
import { VuetifyResolver } from "unplugin-vue-components/resolvers";
import Components from "unplugin-vue-components/vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        createVuePlugin(),
        Components({
            resolvers: [VuetifyResolver()],
        }),
    ],
});
