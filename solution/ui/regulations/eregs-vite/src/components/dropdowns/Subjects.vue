<script setup>
import { computed, ref } from "vue";

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
</script>

<template>
    <GenericDropdown
        class="filter__select--subjects"
        data-testid="subjects-select"
        label="Choose Subject"
        :loading="loading"
        :items="list"
        item-title="full_name"
        item-value="id"
    />
</template>

<style></style>
