<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

// What do I want to do?
// 1. Get the data from the API (categories and documents based on the section or subpart)
// 2. Display the data in a tree structure using existing components



</script>

<template>
    <div class="skeleton">This is the internal docs container.</div>
</template>

<style></style>

