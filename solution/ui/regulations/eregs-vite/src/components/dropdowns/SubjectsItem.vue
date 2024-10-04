<script setup>
import { computed, ref } from "vue";

import { getSubjectName } from "utilities/filters";

const props = defineProps({
    item: {
        type: Object,
        default: () => ({}),
    },
    scopedProps: {
        type: Object,
        default: () => ({}),
    },
});

const getCounts = (item) =>
    item.raw.public_resources + item.raw.internal_resources;

const getTitle = (item) => getSubjectName(item.raw);

const scopedPropsClone = { ...props.scopedProps };

delete scopedPropsClone.title;
</script>

<template>
    <v-list-item v-bind="scopedPropsClone" :value="item.raw.id">
        <v-list-item-content>
            <v-list-item-title>
                {{ getTitle(item) }}
            </v-list-item-title>
        </v-list-item-content>
        <template #append>({{ getCounts(item) }})</template>
    </v-list-item>
</template>

<style></style>
