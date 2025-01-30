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
    <div class="toc-title__container">
        <h2 class="toc-title__heading">
            {{ title }}
        </h2>
        <h3 v-if="subheading" class="toc-title__subheading">
            {{ subheading }}
        </h3>
    </div>
</template>
