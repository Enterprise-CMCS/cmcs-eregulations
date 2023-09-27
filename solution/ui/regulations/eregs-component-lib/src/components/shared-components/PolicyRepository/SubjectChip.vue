<script setup>
const props = defineProps({
    subjectName: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="subject__chip">{{ subjectName }}</div>
</template>
