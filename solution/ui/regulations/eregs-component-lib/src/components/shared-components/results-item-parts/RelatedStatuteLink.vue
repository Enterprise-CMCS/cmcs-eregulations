<script setup>
defineProps({
    title: {
        type: String,
        required: true,
    },
    section: {
        type: Object,
        required: true,
    },
    url: {
        type: String,
        default: undefined,
    },
});

</script>

<template>
    <a
        v-if="url"
        :href="url"
        target="_blank"
        rel="noopener noreferrer"
        class="related-statute__link"
    >
        {{ section }}
    </a>
    <span v-else class="related-statute__span">
        {{ section }}
    </span>
</template>
