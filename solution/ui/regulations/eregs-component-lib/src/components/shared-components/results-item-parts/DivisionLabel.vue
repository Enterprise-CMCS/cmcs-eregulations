<script setup>
import { computed } from "vue";

const props = defineProps({
    division: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <span
        class="result__context--date--bar result__context--division"
        :title="`${division.group.name} — ${division.name}`"
        >Uploaded by {{ division.group.abbreviation }} —
        {{ division.abbreviation }}</span
    >
</template>
