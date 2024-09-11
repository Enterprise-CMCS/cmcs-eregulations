<script setup>
import { inject, onBeforeMount, onMounted, onUnmounted, ref, watch } from "vue";

import useRemoveList from "composables/removeList";

import _isUndefined from "lodash/isUndefined";

import { useRoute, useRouter } from "vue-router";

import { DOCUMENT_TYPES_MAP } from "utilities/utils";

import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";

const removeList = inject("commonRemoveList", []);

const catTypeDict = {
    categories: "external",
    intcategories: "internal",
};

const props = defineProps({
    error: {
        type: Object,
        default: () => {},
    },
    list: {
        type: Array,
        required: true,
    },
    loading: {
        type: Boolean,
        default: true,
    },
    parent: {
        type: String,
        default: "subjects",
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
        silentReset.value = true;
        selectedId.value = `${categories}-categories`;
    } else if (intcategories) {
        silentReset.value = true;
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
        const docTypeObj = {};

        if (newValue) {
            const [id, categoryType] = newValue.split("-");
            categoriesObj[categoryType] = id;

            if (isAuthenticated) {
                docTypeObj.type = catTypeDict[categoryType];
            }
        }

        if (silentReset.value) {
            silentReset.value = false;
            return;
        }

        const routeClone = { ...$route.query };

        const cleanedRoute = useRemoveList({
            route: routeClone,
            removeList,
        });

        $router.push({
            name: props.parent,
            query: {
                ...cleanedRoute,
                ...categoriesObj,
                ...docTypeObj,
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

// popstate to update the select on back/forward click
const onPopState = (event) => {
    const currentPopState = event?.state?.current ?? "";

    const isIntcategories = currentPopState.includes("intcategories");
    const isCategories =
        !isIntcategories && currentPopState.includes("categories");

    silentReset.value = true;

    if (isIntcategories) {
        // use regex to find a number of any length in a string that has the following pattern:
        // subjects?subjects=2&intcategories=3
        const intcategories = currentPopState.match(
            /(?<=intcategories=)\d+/
        )[0];
        selectedId.value = `${intcategories}-intcategories`;
    } else if (isCategories) {
        // use regex to find a number of any length in a string that has the following pattern:
        // subjects?subjects=2&categories=3
        const categories = currentPopState.match(/(?<=categories=)\d+/)[0];
        selectedId.value = `${categories}-categories`;
    }
};

onMounted(() => {
    window.addEventListener("popstate", onPopState);
});

onUnmounted(() => window.removeEventListener("popstate", onPopState));

const onMenuUpdate = () => {
    // if we're toggling the menu via click or kb event,
    // we are not being silent
    if (silentReset.value) silentReset.value = false;
};
</script>

<template>
    <v-select
        v-model="selectedId"
        class="filter__select filter__select--category"
        data-testid="category-select"
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
        @update:menu="onMenuUpdate"
    >
        <template #item="{ props, item }">
            <v-list-item
                v-bind="props"
                :data-testid="`${catTypeDict[item.raw.categoryType]}-${
                    item.raw.catIndex
                }`"
            >
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
