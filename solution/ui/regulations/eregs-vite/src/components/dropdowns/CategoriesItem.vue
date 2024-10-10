<script setup>
import { inject } from "vue";

import { DOCUMENT_TYPES_MAP } from "utilities/utils";

import DocTypeLabel from "sharedComponents/results-item-parts/DocTypeLabel.vue";

defineProps({
    item: {
        type: Object,
        default: () => ({}),
    },
    scopedProps: {
        type: Object,
        default: () => ({}),
    },
});

const isAuthenticated = inject("isAuthenticated");
const catTypeDict = inject("catTypeDict");
</script>

<template>
    <v-list-item v-bind="scopedProps">
        <v-list-item-content>
            <DocTypeLabel
                v-if="isAuthenticated && item.raw.catIndex == 0"
                :class="`doc-type__label--${catTypeDict[item.raw.categoryType]}`"
                :icon-type="catTypeDict[item.raw.categoryType]"
                :doc-type="
                    DOCUMENT_TYPES_MAP[catTypeDict[item.raw.categoryType]]
                "
            />
        </v-list-item-content>
    </v-list-item>
</template>

<style></style>
