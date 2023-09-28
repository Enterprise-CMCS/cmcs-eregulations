import Vue from "vue";
import VueRouter from "vue-router";
import CacheExplorer from "../views/CacheExplorer.vue";
import PolicyRepository from "../views/PolicyRepository.vue";
import PolicyRepositorySearch from "../views/PolicyRepositorySearch.vue";
import Resources from "../views/Resources.vue";
import Search from "../views/Search.vue";
import Statutes from "../views/Statutes.vue";

Vue.use(VueRouter);

const routes = [
    {
        path: "/cache",
        name: "cache",
        component: CacheExplorer,
    },
    {
        path: "/policy-repository",
        name: "policy-repository",
        component: PolicyRepository,
    },
    {
        path: "/policy-repository/search",
        name: "policy-repository-search",
        component: PolicyRepositorySearch,
    },
    {
        path: "/resources",
        name: "resources",
        component: Resources,
    },
    {
        path: "/search",
        name: "search",
        component: Search,
    },
    {
        path: "/statutes",
        name: "statutes",
        component: Statutes,
    },
];

const router = ({ customUrl = "", host = "" }) =>
    new VueRouter({
        mode: "history",
        routes,
        base:
            import.meta.env.VITE_ENV === "prod" && host === customUrl
                ? "/"
                : import.meta.env.VITE_ENV || "/",
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
