<script setup>
defineProps({
    title: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="toc-title__container">
        <h2 class="toc-title__heading">
            {{ title }}
        </h2>
    </div>
</template>
