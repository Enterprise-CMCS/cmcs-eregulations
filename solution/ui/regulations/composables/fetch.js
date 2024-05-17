import { ref } from "vue";

export default function useFetch({ method, apiUrl, cacheResponse = true }) {
    const responseObj = ref({
        data: [],
        error: null,
        loading: true,
    });

    method(apiUrl, cacheResponse)
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
