<script>
// https://stackoverflow.com/a/70947352
// https://vuejs.org/api/sfc-script-setup.html#usage-alongside-normal-script
const itemTypes = {
    categories: useCategories,
    subjects: (paramsObj) => useFetch({ method: getSubjects, ...paramsObj }),
};

export default {};
</script>

<script setup>
import { inject, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";

import { getSubjects } from "utilities/api";

import useCategories from "composables/categories";
import useCounts from "composables/counts";
import useFetch from "composables/fetch";

const props = defineProps({
    itemsToFetch: {
        validator: (value) => {
            return itemTypes[value] !== undefined;
        },
        default: "categories",
    },
    itemsCaptureFunction: {
        type: Function,
        required: false,
        default: () => {},
    },
    includeCounts: {
        type: Boolean,
        default: false,
    },
});

const apiUrl = inject("apiUrl");
const isAuthenticated = inject("isAuthenticated");

const $route = useRoute();

const { counts, fetchCounts } = useCounts();

const results = itemTypes[props.itemsToFetch]({
    apiUrl: apiUrl,
    isAuthenticated,
});

const isLoading = () => {
    if (props.includeCounts) {
        return results.value.loading || counts.value.loading;
    }

    return results.value.loading;
};

watch(
    () => $route.query,
    async (newQueryParams) => {
        const { q } = newQueryParams;

        if (q && props.includeCounts) {
            fetchCounts({
                apiUrl,
                queryParams: { q },
            });
        }
    },
    { immediate: true }
);

watchEffect(() => {
    if (results.value.data) {
        props.itemsCaptureFunction(results.value.data);
    }
});
</script>

<template>
    <slot
        :data="results.data"
        :counts="counts.results[itemsToFetch] || []"
        :error="results.error || counts.error"
        :loading="isLoading()"
    ></slot>
</template>

<style></style>
