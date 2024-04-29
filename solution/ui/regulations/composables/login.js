// https://vuejs.org/guide/reusability/composables
import { ref, onMounted, onUnmounted, watch } from "vue";

export default function useLoginRedirectUrl({
    customLoginUrl,
    homeUrl,
    route,
}) {
    const loginUrl = ref(customLoginUrl);

    const setLoginUrl = () => {
        let basePath;
        let fullPath;
        let redirectUrl;

        if (route) {
            basePath = route.path.substring(1);
            fullPath = route.fullPath;
            redirectUrl = `${customLoginUrl}?next=${homeUrl}${basePath}`;
        } else {
            basePath = window.location.pathname.substring(1);
            fullPath = window.location.href;
            redirectUrl = `${customLoginUrl}?next=${homeUrl}${basePath}`;
        }

        if (!fullPath.includes("?")) {
            if (fullPath.includes("#")) {
                loginUrl.value = `${redirectUrl}${window.location.hash}`;
                return;
            }

            loginUrl.value = redirectUrl;
            return;
        }

        const pathQuery = fullPath.split("?")[1];

        if (pathQuery.length == 0) {
            loginUrl.value = redirectUrl;
            return;
        }

        loginUrl.value = `${redirectUrl}?${pathQuery}`;
    };

    onMounted(() => {
        if (!route) window.addEventListener("hashchange", setLoginUrl);
        setLoginUrl();
    });

    onUnmounted(() => {
        window.removeEventListener("hashchange", setLoginUrl);
    });

    watch(
        () => route?.query,
        async () => {
            setLoginUrl();
        }
    );

    return loginUrl;
}
