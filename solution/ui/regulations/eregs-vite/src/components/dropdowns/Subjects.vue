<script setup>
import { computed, ref } from "vue";

import { getSubjectName } from "utilities/filters";

import GenericDropdown from "./GenericDropdown.vue";

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

const itemProps = (item) => ({
    value: item.id,
    title: getSubjectName(item),
});
</script>

<template>
    <GenericDropdown
        class="filter__select--subjects"
        data-testid="subject-select"
        item-type="SubjectsItem"
        label="Choose Subject"
        :loading="loading"
        :items="list"
        :item-props="itemProps"
    />
</template>

<style></style>
