<script setup>
import { locationLabel, locationUrl } from "utilities/filters";

defineProps({
    citation: {
        type: Object,
        required: true,
    },
    base: {
        type:String,
        required: true,
    },
});
</script>

<template>
    <a
        :href="locationUrl(citation, base)"
        class="related-regulation__link"
    >{{
        locationLabel(citation)
    }}</a>
</template>
