import { ref } from "vue";

import useFetch from "./fetch";

import { getCombinedContent, getContentWithoutQuery } from "utilities/api";
import { DOCUMENT_TYPES_MAP } from "utilities/utils";

export default function useSearchResults() {
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
    }) => {
        policyDocList.value.loading = true;
        policyDocList.value.error = false;

        const requestParams = `${requestParamString}&page_size=${pageSize}&group_resources=false`;
        const docType = type ? DOCUMENT_TYPES_MAP[type] : undefined;

        let contentList;

        try {
            if (query) {
                contentList = await getCombinedContent({
                    apiUrl,
                    requestParams,
                    docType,
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

    return { policyDocList, getDocList };
}
