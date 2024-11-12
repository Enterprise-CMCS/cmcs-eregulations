<template>
    <div class="direction-btn" :class="directionClass">
        <span class="label">{{ label }}</span>
        <span class="icon">
            <i class="fa" :class="chevronClass"></i>
        </span>
    </div>
</template>

<script>
export default {
    name: "NavBtn",

    components: {},

    props: {
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
    },

    computed: {
        chevronClass() {
            return this.direction === "forward"
                ? "fa-chevron-right"
                : "fa-chevron-left";
        },
        directionClass() {
            return {
                [`${this.direction}-btn`]: true,
                disabled: this.isDisabled,
            };
        },
    },
};
</script>
