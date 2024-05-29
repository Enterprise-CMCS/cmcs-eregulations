<script setup>
import { inject, onBeforeMount, ref, watch } from "vue";

import _isUndefined from "lodash/isUndefined";

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
const silentReset = ref(false);

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
        const categoriesObj = {};

        const { categories, intcategories, ...restOfRoute } = $route.query;

        if (newValue) {
            const [id, categoryType] = newValue.split("-");
            categoriesObj[categoryType] = id;
        }

        if (silentReset.value) {
            silentReset.value = false;
            return;
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

watch(
    () => $route.query,
    (newQueryParams, oldQueryParams) => {
        const {
            categories: newCategories,
            intcategories: newIntcategories,
        } = newQueryParams;
        const {
            categories: oldCategories,
            intcategories: oldIntcategories,
        } = oldQueryParams;

        if (
            (oldCategories && newIntcategories) ||
            (oldIntcategories && newCategories)
        ) {
            return;
        }

        // Other components are already scrubbing categories from route;
        // Silently reset selectedId so that route change doesn't trigger
        // a route update and a subsequent re-fetch of content-search
        if (
            (_isUndefined(newCategories) && newCategories !== oldCategories) ||
            (_isUndefined(newIntcategories) &&
                newIntcategories !== oldIntcategories)
        ) {
            silentReset.value = true;
            selectedId.value = undefined;
        }
    }
);
</script>

<template>
    <v-select
        v-model="selectedId"
        class="filter__select filter__select--category"
        variant="outlined"
        clearable
        persistent-clear
        single-line
        hide-details
        flat
        clear-icon="mdi-close"
        menu-icon="mdi-menu-swap"
        label="Choose Category"
        density="compact"
        :loading="loading"
        :disabled="loading"
        :items="list"
        :item-props="itemProps"
    >
        <template #item="{ props, item }">
            <v-list-item v-bind="props">
                <DocTypeLabel
                    v-if="isAuthenticated && item.raw.catIndex == 0"
                    :class="`doc-type__label--${
                        catTypeDict[item.raw.categoryType]
                    }`"
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
