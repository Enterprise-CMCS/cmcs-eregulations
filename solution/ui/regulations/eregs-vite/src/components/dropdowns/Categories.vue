<script setup>
import { computed, ref } from "vue";

const props = defineProps({
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
</script>

<template>
    <v-select
        label="Choose Category"
        :loading="loading"
        density="compact"
        :items="list.map((category) => category.name)"
        variant="outlined"
    ></v-select>
</template>

<style></style>
