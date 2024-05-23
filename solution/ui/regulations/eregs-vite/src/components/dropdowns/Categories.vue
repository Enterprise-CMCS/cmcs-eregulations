<script setup>
import { computed, watch } from "vue";

import { useRoute, useRouter } from "vue-router";

const props = defineProps({
    list: {
        type: Array,
        required: true,
    },
    error: {
        type: Object,
        default: () => {},
    },
    loading: {
        type: Boolean,
        default: true,
    },
});

const $route = useRoute();
const $router = useRouter();

const selectedId = defineModel("id");

const itemProps = (item) => ({
    value: `${item.id}-${item.categoryType}`,
    title: item.name,
});

watch(
    () => selectedId.value,
    (newValue) => {
        let categoriesObj = {};

        const {
            categories,
            internal_categories,
            ...restOfRoute
        } = $route.query;

        if (newValue) {
            const [id, categoryType] = newValue.split("-");
            categoriesObj = {
                [categoryType]: id,
            };
        }

        $router.push({
            name: "subjects",
            query: {
                ...restOfRoute,
                ...categoriesObj,
            },
        });
    }
);
</script>

<template>
    <v-select
        v-model="selectedId"
        clearable
        label="Choose Category"
        :loading="loading"
        density="compact"
        :items="list"
        :item-props="itemProps"
        variant="outlined"
    ></v-select>
</template>

<style></style>
