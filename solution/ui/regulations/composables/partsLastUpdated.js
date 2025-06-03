import { ref } from "vue";

import { getLastUpdatedDates, getTitles } from "utilities/api.js";

export default function usePartsLastUpdated() {
    const partsLastUpdated = ref({
        results: {},
        loading: true,
        error: false,
    });

    const getPartsLastUpdated = async ({ apiUrl }) => {
        partsLastUpdated.value.loading = true;
        partsLastUpdated.value.error = false;

        try {
            const titles = await getTitles({ apiUrl });
            partsLastUpdated.value.results = await getLastUpdatedDates({
                apiUrl,
                titles,
            });
        } catch (error) {
            partsLastUpdated.value.error = true;
            partsLastUpdated.value.results = {};
        } finally {
            partsLastUpdated.value.loading = false;
        }
    };

    return { partsLastUpdated, getPartsLastUpdated };
}
