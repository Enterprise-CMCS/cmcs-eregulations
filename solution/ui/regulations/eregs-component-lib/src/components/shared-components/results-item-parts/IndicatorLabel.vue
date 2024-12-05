<script setup>
const props = defineProps({
    grouped: {
        type: Boolean,
        default: false,
    },
    type: {
        type: String,
        required: true,
    },
});

const indicatorClasses = computed(() => {
    if (props.type === "WD") {
        return {
            "tertiary-indicator": props.type === "WD",
        };
    }
    return {
        "secondary-indicator": props.grouped || props.type !== "Final",
    };
});
</script>

<template>
    <span class="recent-flag indicator" :class="indicatorClasses">{{
        type
    }}</span>
</template>
