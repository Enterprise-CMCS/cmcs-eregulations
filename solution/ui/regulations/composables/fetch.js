import { ref } from "vue";

export default function useFetch({
    method,
    apiUrl,
    cacheResponse = true,
    needsAuthentication = false,
    isAuthenticated = false,
}) {
    const responseObj = ref({
        data: [],
        error: null,
        loading: true,
    });

    if (needsAuthentication && !isAuthenticated) {
        responseObj.value.loading = false;
        return responseObj;
    }

    method({ apiUrl, cacheResponse })
        .then((response) => {
            responseObj.value.data = response;
        })
        .catch((err) => {
            responseObj.value.error = err;
        })
        .finally(() => {
            responseObj.value.loading = false;
        });

    return responseObj;
}