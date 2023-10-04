<script setup>
const props = defineProps({
    page: {
        type: String,
        required: true,
    },
});

console.log("props in ResultItem.vue", props);
</script>

<template>
    <div class="result">
        <div class="category-labels">
            <slot name="labels"></slot>
        </div>
        <div class="result__context">
            <slot name="context"></slot>
        </div>
        <div class="result__link">
            <slot name="link"></slot>
        </div>
        <div class="result__snippet">
            <slot name="snippet"></slot>
        </div>
        <slot name="resources-content"></slot>
        <slot name="chips"></slot>
        <slot name="sections"></slot>
    </div>
</template>

<style></style>
