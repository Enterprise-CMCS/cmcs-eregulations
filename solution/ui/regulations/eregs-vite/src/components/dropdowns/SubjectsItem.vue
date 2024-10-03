<script setup>
import { computed, ref } from "vue";

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

</script>

<template>
    <div class="skeleton"></div>
</template>

<style></style>

