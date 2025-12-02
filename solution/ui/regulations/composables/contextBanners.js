import { ref } from "vue";

import { getContextBanners } from "utilities/api.js";

export default function useContextBanners() {
    const contextBanners = ref({
        results: [],
        loading: false,
        error: false,
    });

    const fetchBanners = async ({
        apiUrl,
        title,
        part,
        sectionKey,
        subparts,
    }) => {
        contextBanners.value.loading = true;
        contextBanners.value.error = false;

        try {
            const params = new URLSearchParams();

            params.set("title", String(title));
            params.set("part", String(part));

            if (sectionKey) {
                params.set("section", sectionKey);
            } else if (subparts && subparts.length === 1) {
                params.set("subpart", String(subparts[0]));
            }

            const resp = await getContextBanners({
                apiUrl,
                requestParams: params.toString(),
            });

            contextBanners.value.results = resp.results ?? [];
        } catch (_error) {
            contextBanners.value.error = true;
            contextBanners.value.results = [];
        } finally {
            contextBanners.value.loading = false;
        }
    };

    return { contextBanners, fetchBanners };
}
