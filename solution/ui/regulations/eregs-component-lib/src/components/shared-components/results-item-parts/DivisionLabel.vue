<script setup>
defineProps({
    division: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <span
        class="result__context--division result__context--division--bar"
        :title="`${division?.group?.name} — ${division?.name}`"
        data-testid="division-label"
    >Uploaded by {{ division?.group?.abbreviation }} —
        {{ division?.abbreviation }}</span>
</template>
