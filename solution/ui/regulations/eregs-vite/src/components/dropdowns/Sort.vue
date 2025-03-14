<script setup>
import { watch } from "vue";

import { useRoute, useRouter } from "vue-router";

import GenericDropdown from "./GenericDropdown.vue";

defineProps({
});

const $route = useRoute();
const $router = useRouter();

const selectedSortMethod = defineModel({ default: "default", type: String });

const sortOptions = [
    { method: "default", label: "Relevance" },
    { method: "desc", label: "Newest" },
    { method: "asc", label: "Oldest" },
];

watch(
    () => $route.query,
    (queryParams) => {
        const { sort } = queryParams;

        if (sort) {
            selectedSortMethod.value = sort;
        } else {
            selectedSortMethod.value = "default";
        }
    },
    { immediate: true }
);

watch(
    selectedSortMethod,
    (newValue) => {
        $router.push({
            name: "search",
            query: {
                ...$route.query,
                sort: newValue,
            },
        });
    }
)

</script>

<template>
    <GenericDropdown
        v-model="selectedSortMethod"
        class="filter__select--sort"
        :clearable="false"
        data-testid="sort-select"
        :items="sortOptions"
        item-title="label"
        item-value="method"
    />
</template>

<style></style>
