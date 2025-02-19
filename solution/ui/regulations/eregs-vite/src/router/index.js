import { createRouter, createWebHistory } from "vue-router";
import Search from "../views/Search.vue";
import Statutes from "../views/Statutes.vue";
import Subjects from "../views/Subjects.vue";

const routes = [
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
    {
        path: "/subjects",
        name: "subjects",
        component: Subjects,
        props: true,
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
