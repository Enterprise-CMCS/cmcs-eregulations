<script setup>
import { inject, onBeforeMount, watch } from "vue";

import { useRoute, useRouter } from "vue-router";

import { DOCUMENT_TYPES_MAP } from "utilities/utils";

import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";

const catTypeDict = {
    categories: "external",
    intcategories: "internal",
};

defineProps({
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

const isAuthenticated = inject("isAuthenticated");

const $route = useRoute();
const $router = useRouter();

const selectedId = defineModel("id");

onBeforeMount(() => {
    const { categories, intcategories } = $route.query;

    if (categories) {
        selectedId.value = `${categories}-categories`;
    } else if (intcategories) {
        selectedId.value = `${intcategories}-intcategories`;
    }
});

const itemProps = (item) => ({
    value: `${item.id}-${item.categoryType}`,
    title: item.name,
});

watch(
    () => selectedId.value,
    (newValue) => {
        let categoriesObj = {};
        const { categories, intcategories, ...restOfRoute } = $route.query;

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
        class="subjects__category-select"
        variant="outlined"
        clearable
        persistent-clear
        single-line
        clear-icon="mdi-close"
        menu-icon="mdi-menu-swap"
        label="Choose Category"
        density="compact"
        :loading="loading"
        :items="list"
        :item-props="itemProps"
    >
        <template #item="{ props, item }">
            <v-list-item v-bind="props">
                <DocTypeLabel
                    v-if="isAuthenticated && item.raw.catIndex == 0"
                    :icon-type="catTypeDict[item.raw.categoryType]"
                    :doc-type="
                        DOCUMENT_TYPES_MAP[catTypeDict[item.raw.categoryType]]
                    "
                />
            </v-list-item>
        </template>
    </v-select>
</template>

<style></style>
