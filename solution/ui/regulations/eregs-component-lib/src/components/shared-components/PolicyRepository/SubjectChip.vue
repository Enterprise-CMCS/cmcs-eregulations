<script setup>
import { computed, ref } from "vue";

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
