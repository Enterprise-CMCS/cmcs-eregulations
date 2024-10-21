<script>
// https://stackoverflow.com/a/70947352
// https://vuejs.org/api/sfc-script-setup.html#usage-alongside-normal-script
import { inject, watchEffect } from "vue";

import { getSubjects } from "utilities/api";

import useCategories from "composables/categories";
import useFetch from "composables/fetch";

const itemTypes = {
    categories: useCategories,
    subjects: (paramsObj) => useFetch({ method: getSubjects, ...paramsObj }),
};

export default {};
</script>

<script setup>
const props = defineProps({
    itemsToFetch: {
        validator: (value) => {
            return itemTypes[value] !== undefined;
        },
        default: "categories",
    },
    categoriesCaptureFunction: {
        type: Function,
        required: false,
        default: () => {},
    },
});

const apiUrl = inject("apiUrl");
const isAuthenticated = inject("isAuthenticated");

const results = itemTypes[props.itemsToFetch]({
    apiUrl: apiUrl,
    isAuthenticated,
});

watchEffect(() => {
    if (results.value.data) {
        props.categoriesCaptureFunction(results.value.data);
    }
});
</script>

<template>
    <slot
        :data="results.data"
        :error="results.error"
        :loading="results.loading"
    ></slot>
</template>

<style></style>
