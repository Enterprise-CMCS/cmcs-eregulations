import { ref } from "vue";

import { getStatuteCitationLink } from "utilities/api.js";

export default function useStatuteCitationLink() {
    const statuteCitationInfo = ref({
        results: {},
        loading: false,
        error: false,
    });

    const getStatuteCitationInfo = async ({ apiUrl, citation }) => {
        statuteCitationInfo.value.loading = true;
        statuteCitationInfo.value.error = false;

        try {
            statuteCitationInfo.value.results = await getStatuteCitationLink({
                apiUrl,
                citation,
            });
        } catch (_error) {
            statuteCitationInfo.value.error = true;
            statuteCitationInfo.value.results = {};
        } finally {
            statuteCitationInfo.value.loading = false;
        }
    };

    return { statuteCitationInfo, getStatuteCitationInfo };
}
