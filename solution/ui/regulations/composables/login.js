// https://vuejs.org/guide/reusability/composables
import { ref, watch } from "vue";

// this is garbage Copilot code; use as scaffold only
// Logic assuming that we're in the SPA and vue-router exists
export function useRouterLogin({ customLoginUrl, homeUrl, route }) {
    const loginUrl = ref(customLoginUrl);

    const setLoginUrl = () => {
        const redirectUrl = `${customLoginUrl}?next=${homeUrl}subjects/`;

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

    watch(
        () => route.query,
        async () => {
            setLoginUrl();
        }
    );

    setLoginUrl();

    return loginUrl;
}

// this is garbage Copilot code; use as scaffold only
// Logic assuming that we're in Django and vue-router doesn't exist
export function useWindowLogin() {
    const loginUrl = ref("");

    onMounted(() => {
        loginUrl.value = "/admin";
    });

    onUnmounted(() => {
        loginUrl.value = "";
    });

    return { loginUrl };
}
