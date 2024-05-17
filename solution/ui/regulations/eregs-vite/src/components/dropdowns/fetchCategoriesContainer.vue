<script setup>
import { computed, inject, ref } from "vue";

import useFetch from "composables/fetch";

import { getCategories } from "utilities/api";

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

const categoriesList = useFetch({ method: getCategories, apiUrl });
</script>

<template>
    <div class="skeleton">
        {{ categoriesList.loading ? "Loading..." : "Loaded" }}
        {{ categoriesList.data }}
    </div>
</template>

<style></style>
