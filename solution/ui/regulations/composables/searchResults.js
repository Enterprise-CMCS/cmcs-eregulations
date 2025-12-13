import { ref } from "vue";

import { getSemanticSearchResults, getContentWithoutQuery } from "utilities/api.js";
import { DOCUMENT_TYPES_MAP } from "utilities/utils.js";

function useSearchResults({ getSemanticSearchResults, getContentWithoutQuery }) {
    const policyDocList = ref({
        count: 0,
        results: [],
        loading: true,
        error: false,
    });

    const getDocList = async ({
        apiUrl,
        pageSize,
        requestParamString = "",
        query,
        type,
        data,
    }) => {
        policyDocList.value.loading = true;
        policyDocList.value.error = false;

        const requestParams = `${requestParamString}&page_size=${pageSize}&group_resources=false`;
        const docType = type ? DOCUMENT_TYPES_MAP[type] : undefined;

        let contentList;

        try {
            if (query) {
                contentList = await getSemanticSearchResults({
                    apiUrl,
                    data,
                });
            } else {
                contentList = await getContentWithoutQuery({
                    apiUrl,
                    requestParams,
                    docType,
                });
            }

            policyDocList.value.results = contentList.results;
            policyDocList.value.count = contentList.count;
        } catch (error) {
            console.error(error);
            policyDocList.value.results = [];
            policyDocList.value.count = 0;
            policyDocList.value.error = true;
        } finally {
            policyDocList.value.loading = false;
        }
    };

    const clearDocList = () => {
        policyDocList.value.results = [];
        policyDocList.value.count = 0;
        policyDocList.value.loading = false;
        policyDocList.value.error = false;
    };

    return { policyDocList, getDocList, clearDocList };
}

export default () =>
    useSearchResults({ getSemanticSearchResults, getContentWithoutQuery });
