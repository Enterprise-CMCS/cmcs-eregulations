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
    <div class="sidebar__filters">
        <slot name="title">
            <h2>Find Policy Documents</h2>
        </slot>
        <slot name="filters"></slot>
    </div>
</template>

<style></style>
