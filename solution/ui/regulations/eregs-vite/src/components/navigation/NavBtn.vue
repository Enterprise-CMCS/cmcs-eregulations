<script setup>
import { computed } from "vue";

const props = defineProps({
    direction: {
        type: String,
        required: true,
        default: "forward",
    },
    label: {
        type: String,
        required: true,
        default: "Loading...",
    },
    isDisabled: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const chevronClass = computed(() => {
    return props.direction === "forward"
        ? "fa-chevron-right"
        : "fa-chevron-left";
});

const directionClass = computed(() => {
    return {
        [`${props.direction}-btn`]: true,
        disabled: props.isDisabled,
    };
});
</script>

<template>
    <div class="direction-btn" :class="directionClass">
        <span class="label">{{ label }}</span>
        <span class="icon">
            <i class="fa" :class="chevronClass" />
        </span>
    </div>
</template>
