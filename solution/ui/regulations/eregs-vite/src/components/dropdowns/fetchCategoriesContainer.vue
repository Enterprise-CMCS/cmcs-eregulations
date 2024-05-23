<script setup>
import { computed, inject, ref } from "vue";

import useFetch from "composables/fetch";

import { getExternalCategories } from "utilities/api";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    filterList: {
        type: Array,
        default: () => [],
    },
});

const apiUrl = inject("apiUrl");

const categoriesList = useFetch({ method: getExternalCategories, apiUrl });
</script>

<template>
    <slot
        :data="categoriesList.data"
        :error="categoriesList.error"
        :loading="categoriesList.loading"
    ></slot>
</template>

<style></style>
