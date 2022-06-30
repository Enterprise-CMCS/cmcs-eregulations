import Vue from "vue";
import VueRouter from "vue-router";
import Home from "@/views/Home.vue";
import Part from "@/views/Part.vue";
import Resources from "@/views/Resources.vue";
import CacheExplorer from "@/views/CacheExplorer";
import PDPart from "@/views/PDPart";
import ResourcePage from "@/views/ResourcePage"

Vue.use(VueRouter);

const routes = [
    {
        path: "/",
        name: "home",
        component: Home,
    },
    {
        path: "/about",
        name: "about",
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () =>
            import(/* webpackChunkName: "about" */ "../views/About.vue"),
    },
    {
        path: "/zoom/:title/:part/:subPart/:section",
        name: "PDpart-section",
        component: PDPart,
    },
        {
        path: "/zoom/:title/:part/:subPart",
        name: "PDpart-subPart",
        component: PDPart,
    },
        {
        path: "/zoom/:title/:part",
        name: "PDpart",
        component: PDPart,
    },
    {
        path: "/:title/:part/:tab?", // tab will be "toc", "subpart", or "section". default: "part"
        name: "part",
        component: Part,
    },
    {
        path: "/resources",
        name: "resources",
        component: Resources,
    },
    {
        path: "/resources-sidebar",
        name: "resources-sidebar",
        component: Resources,
    },
    {
        path: "/cache",
        name: "Cache-Explorer",
        component: CacheExplorer,
    },
    {
        path: "/PDResources",
        name: "PDResources",
        component: ResourcePage
    }
];

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
    scrollBehavior: function (to) {
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
