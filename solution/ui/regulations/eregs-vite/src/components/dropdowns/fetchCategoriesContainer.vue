<script setup>
import { inject, watchEffect } from "vue";

import useCategories from "composables/categories";

const props = defineProps({
    categoriesCaptureFunction: {
        type: Function,
        required: false,
        default: () => {},
    },
});

const apiUrl = inject("apiUrl");
const isAuthenticated = inject("isAuthenticated");

const combinedCategories = useCategories({
    apiUrl: apiUrl,
    isAuthenticated,
});

watchEffect(() => {
    if (combinedCategories.value.data) {
        props.categoriesCaptureFunction(combinedCategories.value.data);
    }
});
</script>

<template>
    <slot
        :data="combinedCategories.data"
        :error="combinedCategories.error"
        :loading="combinedCategories.loading"
    ></slot>
</template>

<style></style>
