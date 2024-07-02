import { ref } from "vue";
import _isArray from "lodash/isArray";

export default function useFetch({
    method,
    apiUrl,
    cacheResponse,
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
            responseObj.value.data = _isArray(response)
                ? response
                : response.results;
        })
        .catch((err) => {
            responseObj.value.error = err;
        })
        .finally(() => {
            responseObj.value.loading = false;
        });

    return responseObj;
}
