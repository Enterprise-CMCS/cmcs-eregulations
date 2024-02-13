import Vue from "vue";
import VueRouter from "vue-router";

const { isNavigationFailure, NavigationFailureType } = VueRouter;

import vuetify from "./plugins/vuetify";
import App from "./App.vue";
import vueRouter from "./router";

import Clickaway from "./directives/clickaway";

const mountEl = document.querySelector("#vite-app");
Vue.config.devtools = true;
const { customUrl, host } = mountEl.dataset;

let { isAuthenticated } = mountEl.dataset;
isAuthenticated = isAuthenticated === "True";

Vue.directive("clickaway", Clickaway);

const router = vueRouter({ customUrl, host });

router.beforeEach((to, from, next) => {
    if (!isAuthenticated && to.name === "subjects" && to.query?.type) {
        const { type, ...query } = to.query;
        next({ ...to, query });
    } else {
        next();
    }
});

// Silence duplicate navigation errors
// see:
// - https://stackoverflow.com/questions/57837758/navigationduplicated-navigating-to-current-location-search-is-not-allowed
// - https://github.com/vuejs/vue-router/issues/2872
const originalPush = router.push;
router.push = function push(location, onResolve, onReject) {
    if (onResolve || onReject) {
        return originalPush.call(this, location, onResolve, onReject);
    }

    return originalPush.call(this, location).catch((err) => {
        if (isNavigationFailure(err, NavigationFailureType.duplicated)) {
            return err;
        }

        return Promise.reject(err);
    });
};

new Vue({
    vuetify,
    router,
    render: (h) => h(App, { props: { ...mountEl.dataset } }),
}).$mount("#vite-app");
