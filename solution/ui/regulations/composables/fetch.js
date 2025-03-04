import { ref } from "vue";

export default function useFetch({
    method,
    apiUrl,
    needsAuthentication = false,
    isAuthenticated = false,
    args,
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

    method({ apiUrl, args })
        .then((response) => {
            responseObj.value.data = Array.isArray(response)
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
