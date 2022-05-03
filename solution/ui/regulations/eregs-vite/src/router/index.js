import Vue from "vue";
import VueRouter from "vue-router";
import CacheExplorer from "../views/CacheExplorer.vue";

Vue.use(VueRouter);

const routes = [
    {
        path: "/cache",
        name: "cache",
        component: CacheExplorer,
    }
]

const router = new VueRouter({
    mode: "history",
    routes,
    scrollBehavior(to) {
        if (to.hash) {
            return {
                selector: to.hash,
                offset: { x: 0, y: 80 },
            };
        }
        return { x: 0, y: 0 };
    },
});

export default router;
