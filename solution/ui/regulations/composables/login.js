// https://vuejs.org/guide/reusability/composables
import { ref, onMounted, watch } from "vue";

// this is garbage Copilot code; use as scaffold only
// Logic assuming that we're in the SPA and vue-router exists
export function useRouterLogin({ customLoginUrl, homeUrl, route }) {
    const loginUrl = ref(customLoginUrl);

    const setLoginUrl = () => {
        const redirectUrl = `${customLoginUrl}?next=${homeUrl}${route.path.substring(
            1
        )}`;

        if (!route.fullPath.includes("?")) {
            loginUrl.value = redirectUrl;
            return;
        }

        const pathQuery = route.fullPath.split("?")[1];

        if (pathQuery.length == 0) {
            loginUrl.value = redirectUrl;
            return;
        }

        loginUrl.value = `${redirectUrl}?${pathQuery}`;
    };

    onMounted(() => {
        setLoginUrl();
    });

    watch(
        () => route.query,
        async () => {
            setLoginUrl();
        }
    );

    return loginUrl;
}

// this is garbage Copilot code; use as scaffold only
// Logic assuming that we're in Django and vue-router doesn't exist
export function useWindowLogin({ customLoginUrl, homeUrl }) {
    const loginUrl = ref(customLoginUrl);

    const setLoginUrl = () => {
        const redirectUrl = `${customLoginUrl}?next=${homeUrl}${window.location.pathname.substring(
            1
        )}`;

        if (!window.location.href.includes("?")) {
            loginUrl.value = redirectUrl;
            return;
        }

        const pathQuery = window.location.href.split("?")[1];

        if (pathQuery.length == 0) {
            loginUrl.value = redirectUrl;
            return;
        }

        loginUrl.value = `${redirectUrl}?${pathQuery}`;
    };

    onMounted(() => {
        setLoginUrl();
    });

    watch(
        () => window.location,
        async () => {
            setLoginUrl();
        }
    );

    return loginUrl;
}
