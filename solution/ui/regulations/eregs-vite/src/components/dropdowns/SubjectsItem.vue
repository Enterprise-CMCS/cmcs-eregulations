<script setup>
import { computed, ref } from "vue";

import { getSubjectName } from "utilities/filters";

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

const getCounts = (item) =>
    item.raw.public_resources + item.raw.internal_resources;

const getTitle = (item) => getSubjectName(item.raw);
</script>

<template>
    <v-list-item
        v-bind="scopedProps"
        :title="getTitle(item)"
        :value="item.raw.id"
    >
        <template #append>({{ getCounts(item) }})</template>
    </v-list-item>
</template>

<style></style>
