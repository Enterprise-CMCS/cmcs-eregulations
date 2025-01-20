// https://vuejs.org/guide/reusability/composables
import { ref, onMounted, onUnmounted, watch } from "vue";

export default function useLoginRedirectUrl({
    customLoginUrl,
    homeUrl,
    route,
    directLink = undefined,
}) {
    const loginUrl = ref(customLoginUrl);

    const setLoginUrl = () => {
        let basePath;
        let fullPath = "no-url-params";
        let redirectUrl;

        if (route) {
            basePath = route.path.substring(1);
            fullPath = route.fullPath;
            redirectUrl = `${customLoginUrl}?next=${homeUrl}${basePath}`;
        } else if (directLink) {
            redirectUrl = `${customLoginUrl}?next=${directLink}`;
        } else {
            basePath = window.location.pathname;
            fullPath = window.location.href;
            redirectUrl = `${customLoginUrl}?next=${basePath}`;
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
