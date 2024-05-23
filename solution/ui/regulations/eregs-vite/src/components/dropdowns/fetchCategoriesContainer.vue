<script setup>
import { inject, ref, watchEffect } from "vue";

import useFetch from "composables/fetch";

import {
    getExternalCategoriesTree,
    getInternalCategoriesTree,
} from "utilities/api";

defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
});

const apiUrl = inject("apiUrl");

const combinedCategories = ref({
    loading: true,
    error: null,
    data: [],
});

const externalCategories = useFetch({
    method: getExternalCategoriesTree,
    apiUrl,
});

const internalCategories = useFetch({
    method: getInternalCategoriesTree,
    apiUrl,
});

// watchEffect: super watch
// https://vuejs.org/guide/essentials/watchers.html#watcheffect
watchEffect(() => {
    combinedCategories.value.loading =
        externalCategories.value.loading || internalCategories.value.loading;

    if (!combinedCategories.value.loading) {
        // move to method
        const externalCats = externalCategories.value.data.map((cat) => ({
            ...cat,
            categoryType: "categories",
        }));
        const internalCats = internalCategories.value.data.map((cat) => ({
            ...cat,
            categoryType: "internal_categories",
        }));
        combinedCategories.value.data = [...externalCats, ...internalCats];
    }
});
</script>

<template>
    <slot
        :data="combinedCategories.data"
        :error="externalCategories.error"
        :loading="combinedCategories.loading"
    ></slot>
</template>

<style></style>
