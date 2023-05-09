<script setup>
    const props = defineProps({
        part: {
            type: Object,
            required: true,
        },
    });
</script>

<template>
    <div class="toc-part-container">
        <h5 class="toc-part-label">{{ part.label_level }} - {{ part.label_description }}</h2>
    </div>
</template>
