<script setup>
import { computed, ref } from "vue";

import { useRoute, useRouter } from "vue-router";

import GenericDropdown from "./GenericDropdown.vue";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

const $route = useRoute();
const $router = useRouter();

const selectedSortMethod = defineModel({ default: "default", type: String });

const sortOptions = [
    { method: "default", label: "Relevance" },
    { method: "desc", label: "Newest" },
    { method: "asc", label: "Oldest" },
];

</script>

<template>
    <GenericDropdown
        v-model="selectedSortMethod"
        class="filter__select--sort"
        :clearable="false"
        data-testid="sort-select"
        :disabled="loading"
        :items="sortOptions"
        item-title="label"
        item-value="method"
    />
</template>

<style></style>
