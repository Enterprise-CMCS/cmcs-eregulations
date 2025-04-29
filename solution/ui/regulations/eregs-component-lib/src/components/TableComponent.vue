<script setup>
import { computed } from 'vue';

const props = defineProps({
    table_markup: {
        type: String,
        required: true,
    },
});

const table = computed(() => props.table_markup);
</script>

<template>
    <section v-sanitize-html="table" class="table-section" />
</template>
