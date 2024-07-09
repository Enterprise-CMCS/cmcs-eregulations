<script setup>
import { inject, ref, watchEffect } from "vue";

import useFetch from "composables/fetch";

import {
    getExternalCategories,
    getInternalCategories,
} from "utilities/api";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    categoriesCaptureFunction: {
        type: Function,
        required: false,
        default: () => {},
    },
});

const apiUrl = inject("apiUrl");
const isAuthenticated = inject("isAuthenticated");

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
    cacheResponse: false,
    needsAuthentication: true,
    isAuthenticated,
});

// watchEffect: super watch
// https://vuejs.org/guide/essentials/watchers.html#watcheffect
watchEffect(() => {
    combinedCategories.value.loading =
        externalCategories.value.loading || internalCategories.value.loading;

    if (!combinedCategories.value.loading) {
        const externalCats = externalCategories.value.data.map((cat, i) => ({
            ...cat,
            categoryType: "categories",
            catIndex: i,
        }));

        const internalCats = internalCategories.value.data.map((cat, i) => ({
            ...cat,
            categoryType: "intcategories",
            catIndex: i,
        }));

        combinedCategories.value.data = [...externalCats, ...internalCats];

        props.categoriesCaptureFunction(combinedCategories.value.data);
    }
});
</script>

<template>
    <slot
        :data="combinedCategories.data"
        :error="externalCategories.error || internalCategories.error"
        :loading="combinedCategories.loading"
    ></slot>
</template>

<style></style>
