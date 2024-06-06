import { createApp } from "vue";
import { isNavigationFailure, NavigationFailureType } from "vue-router";
import Clickaway from "directives/clickaway";
import vuetify from "./plugins/vuetify";

import App from "./App.vue";
import vueRouter from "./router";

import _isArray from "lodash/isArray";

const mountEl = document.querySelector("#vite-app");
const { customUrl, host } = mountEl.dataset;

let { isAuthenticated } = mountEl.dataset;
isAuthenticated = isAuthenticated === "True";

const app = createApp(App, { ...mountEl.dataset });
app.use(vuetify);

app.directive("clickaway", Clickaway);

const router = vueRouter({ customUrl, host });

router.beforeEach((to) => {
    const pageTitle = "Find by Subject | Medicaid & CHIP eRegulations";

    if (to.name === "subjects") {
        if (!to.query?.subject) {
            document.title = pageTitle;
        }

        if (!isAuthenticated && to.query?.type) {
            const { type, ...typelessQuery } = to.query;
            return { name: "subjects", query: typelessQuery };
        }
    }

    return true;
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

app.use(router);
app.mount("#vite-app");
