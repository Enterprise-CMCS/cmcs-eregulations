import Vue from "vue";
import VueRouter from "vue-router";
import CacheExplorer from "../views/CacheExplorer.vue";
import Resources from "../views/Resources.vue";

Vue.use(VueRouter);

const routes = [
    {
        path: "/cache",
        name: "cache",
        component: CacheExplorer,
    },

    {
        path: "/resources",
        name: "resources",
        component: Resources,
    },
];

const router = ({ baseUrl = "", host = "" }) =>
    new VueRouter({
        mode: "history",
        routes,
        base:
            !import.meta.env.VITE_ENV ||
            (import.meta.env.VITE_ENV === "dev578" && host === baseUrl) // VITE_ENV should be "prod"; changing to "dev578" for testing purposes
                ? "/"
                : import.meta.env.VITE_ENV,
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
