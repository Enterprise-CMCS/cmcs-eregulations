<script setup>
import { computed, ref } from "vue";

const props = defineProps({
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
        class="related-section"
    >
        {{ section }}
    </a>
    <span v-else class="related-section">
        {{ section }}
    </span>
</template>
