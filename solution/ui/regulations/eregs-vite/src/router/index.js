import { createRouter, createWebHistory } from "vue-router";
import CacheExplorer from "../views/CacheExplorer.vue";
import PolicyRepository from "../views/PolicyRepository.vue";
import PolicyRepositorySearch from "../views/PolicyRepositorySearch.vue";
import Resources from "../views/Resources.vue";
import Search from "../views/Search.vue";
import Statutes from "../views/Statutes.vue";

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
    createRouter({
        history: createWebHistory(
            import.meta.env.VITE_ENV === "prod" && host === customUrl
                ? "/"
                : import.meta.env.VITE_ENV || "/"
        ),
        routes,
        scrollBehavior(to) {
            if (to.hash) {
                return {
                    selector: to.hash,
                    offset: { left: 0, top: 80 },
                };
            }
            return { left: 0, top: 0 };
        },
    });

export default router;
