import { ref } from "vue";

import { getGranularCounts } from "utilities/api";

import { getRequestParams } from "utilities/utils";

export default function useCounts() {
    const counts = ref({
        results: {},
        loading: true,
        error: false,
    });

    const fetchCounts = async ({ apiUrl, queryParams }) => {
        counts.value.loading = true;
        counts.value.error = false;

        try {
            const response = await getGranularCounts({
                apiUrl,
                requestParams: getRequestParams({ queryParams }),
            });

            counts.value.results = response;
        } catch (error) {
            counts.value.error = true;
            counts.value.results = {};
        } finally {
            counts.value.loading = false;
        }
    };

    return { counts, fetchCounts };
}
