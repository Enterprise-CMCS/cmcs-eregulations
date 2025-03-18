<script setup>
import { ref, watch } from "vue";

import { useRoute, useRouter } from "vue-router";

import GenericDropdown from "./GenericDropdown.vue";

defineProps({
    loading: {
        type: Boolean,
        default: true,
    },
});

const $route = useRoute();
const $router = useRouter();

const selectedSortMethod = defineModel({ default: "default", type: String });

const sortOptions = ref([
    { method: "default", label: "Relevance" },
    { method: "-date", label: "Newest" },
    { method: "date", label: "Oldest" },
]);

const itemProps = (item) => {
    return {
        title: item.label,
        value: item.method,
        disabled: item.disabled
    };
};

watch(
    () => $route.query,
    (queryParams) => {
        const { sort, type } = queryParams;

        if (sort) {
            selectedSortMethod.value = sort;
        } else {
            selectedSortMethod.value = "default";
        }

        // disable all but default sort method for regulations
        if (type && type === "regulations") {
            sortOptions.value
                .filter((option) => option.method !== "default")
                .forEach(option => {
                    option.disabled = true;
                });
        } else {
            sortOptions.value
                .filter((option) => option.method !== "default")
                .forEach(option => {
                    option.disabled = false;
                });
        }
    },
    { immediate: true }
);

watch(
    selectedSortMethod,
    (newValue) => {
        if (newValue === "default") {
            $router.push({
                name: "search",
                query: {
                    ...$route.query,
                    sort: undefined,
                },
            });
            return;
        }

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
        :item-props="itemProps"
        :items="sortOptions"
        :disabled="loading"
    />
</template>
