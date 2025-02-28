<script>
const SPINNER_SIZES = ["xs", "small", "medium", "large"];

export default { SPINNER_SIZES };
</script>

<script setup>
import { computed } from "vue";

const props = defineProps({
    size: {
        validator: (value) => SPINNER_SIZES.includes(value),
        default: "medium",
    },
    filled: {
        type: Boolean,
        default: false,
    },
});

const spinnerClasses = computed(() => ({
    "ds-c-spinner--filled": props.filled,
    "ds-c-spinner--small": props.size === "xs" || props.size === "small",
    "ds-c-spinner--big": props.size === "large",
}));

const spinnerStyles = computed(() => {
    switch (props.size) {
        case "xs":
            return "margin: 0px";
        case "small":
            return "margin: 4px";
        default:
            return "margin: 8px";
    }
});
</script>

<template>
    <div
        class="ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center loading-spinner"
    >
        <span
            class="ds-c-spinner"
            :class="spinnerClasses"
            :style="spinnerStyles"
            role="status"
        >
            <span class="ds-u-visibility--screen-reader">Loading</span>
        </span>
    </div>
</template>
