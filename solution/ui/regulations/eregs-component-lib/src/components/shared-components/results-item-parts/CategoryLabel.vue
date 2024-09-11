<script setup>
import { computed } from "vue";

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        default: "category",
    },
});

const labelClass = computed(() => `${props.type}-label`);
</script>

<template>
    <div class="result-label" :class="labelClass">
        {{ name }}
    </div>
</template>
