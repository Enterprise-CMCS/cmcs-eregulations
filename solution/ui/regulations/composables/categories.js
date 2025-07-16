import { ref, watchEffect } from "vue";

import useFetch from "./fetch";

import { getExternalCategories, getInternalCategories } from "utilities/api";

export default function useCategories({ apiUrl, isAuthenticated = false }) {
    const combinedCategories = ref({
        loading: true,
        error: null,
        data: [],
    });

    const externalCategories = useFetch({
        method: getExternalCategories,
        apiUrl,
    });

    const internalCategories = useFetch({
        method: getInternalCategories,
        apiUrl,
        needsAuthentication: true,
        isAuthenticated,
    });

    // watchEffect: super watch
    // https://vuejs.org/guide/essentials/watchers.html#watcheffect
    watchEffect(() => {
        combinedCategories.value.loading =
            externalCategories.value.loading &&
            internalCategories.value.loading;

        combinedCategories.value.error =
            externalCategories.value.error || internalCategories.value.error;

        if (!combinedCategories.value.loading) {
            const externalCats = externalCategories.value.data.map(
                (cat, i) => ({
                    ...cat,
                    categoryType: "categories",
                    catIndex: i,
                })
            );

            const internalCats = internalCategories.value.data.map(
                (cat, i) => ({
                    ...cat,
                    categoryType: "intcategories",
                    catIndex: i,
                })
            );

            combinedCategories.value.data = [...externalCats, ...internalCats];
        }
    });

    return combinedCategories;
}
