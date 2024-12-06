<script>
const getIndicatorClasses = (props) => {
    if (props.type === "Final") {
        return;
    }

    return {
        "secondary-indicator": props.type !== "WD",
        "tertiary-indicator": props.type === "WD",
    };
};

export default {
    getIndicatorClasses,
};
</script>

<script setup>
import { computed } from "vue";

const props = defineProps({
    type: {
        type: String,
        required: true,
    },
});

const indicatorClasses = computed(() => {
    return getIndicatorClasses(props);
});
</script>

<template>
    <span class="recent-flag indicator" :class="indicatorClasses">{{
        type
    }}</span>
</template>
