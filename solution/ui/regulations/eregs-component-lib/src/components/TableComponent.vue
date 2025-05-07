<script setup>
import { computed } from 'vue';

const props = defineProps({
    tableMarkup: {
        type: String,
        required: true,
    },
});

const table = computed(() => props.tableMarkup);
</script>

<template>
    <section v-sanitize-html="table" class="table-section" />
</template>
