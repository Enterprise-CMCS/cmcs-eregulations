<script setup>
const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    subheading: {
        type: String,
        required: false,
        default: undefined,
    },
});
</script>

<template>
    <div class="toc-title-container">
        <h2 class="toc-title-label">{{ title }}</h2>
        <h3 v-if="subheading" class="toc-title-subheading">{{ subheading }}</h3>
    </div>
</template>
