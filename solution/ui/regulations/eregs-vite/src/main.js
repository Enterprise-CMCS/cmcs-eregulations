import { createApp } from "vue";
import { isNavigationFailure, NavigationFailureType } from "vue-router";
import Clickaway from "directives/clickaway";
import SanitizeHtml from "directives/sanitizeHtml";
import {
    compressQueryString,
} from "utilities/utils.js";
import vuetify from "./plugins/vuetify";

import App from "./App.vue";
import vueRouter from "./router";

const mountEl = document.querySelector("#vite-app");
const { siteRoot, isAuthenticated } = mountEl.dataset;

const app = createApp(App);
app.use(vuetify);

// App-level provide of all data attributes on the mount element
for (const datum in mountEl.dataset) {
    if (mountEl.dataset[datum] === "True") {
        app.provide(datum, true);
    } else if (mountEl.dataset[datum] === "False") {
        app.provide(datum, false);
    } else {
        app.provide(datum, mountEl.dataset[datum]);
    }
}

app.directive("clickaway", Clickaway);
app.directive("sanitize-html", SanitizeHtml);

const router = vueRouter({ siteRoot });

router.beforeEach(async (to) => {
    const pageTitle = "Find by Subject | Medicaid & CHIP eRegulations";

    // If you pass multiple query params in the URL, Vue Router will parse them as arrays.
    // This is a workaround to convert them back to strings -- we only need the first value.
    // `type` is the only query param that should be an array.
    Object.entries(to.query).forEach(([key, value]) => {
        if (Array.isArray(value) && key != "type") {
            to.query[key] = value[0];
        }
    });

    switch (to.name) {
        case "subjects": {
            if (!to.query?.subject) {
                document.title = pageTitle;
            }

            // strip out q param if it exists; it's not needed for subjects
            const { q, ...qlessQuery } = to.query;

            if (isAuthenticated === "False" && to.query?.type) {
                const { type: _type, ...typelessQuery } = qlessQuery;
                return { name: "subjects", query: typelessQuery };
            }

            if (q) {
                return { name: "subjects", query: qlessQuery };
            }
            break;
        }
        case "search": {
            if (
                to.query?.q
                    && to.query.q.length > 5
                    && to.query.compressed !== "true"
            ) {
                let returnQuery = { ...to.query };
                returnQuery.q = compressQueryString(to.query.q);
                returnQuery.compressed = "true";

                return { name: to.name, query: returnQuery };
            }
            break;
        }
        default:
            return true;
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

app.use(router);
app.mount("#vite-app");
