<script setup>
defineProps({
    subheading: {
        type: String,
        required: false,
        default: undefined,
    },
});
</script>

<template>
    <h3 v-if="subheading" class="toc-title__subheading">
        {{ subheading }}
    </h3>
</template>
