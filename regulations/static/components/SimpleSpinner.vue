<template>
    <div
        class="ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center"
    >
        <span
            class="ds-c-spinner"
            :class="spinnerClasses"
            role="status"
            ><span class="ds-u-visibility--screen-reader">Loading</span></span
        >
    </div>
</template>

<script>
export default {
    name: "simple-spinner",

    props: {
        size: {
            type: String,
            default: "medium",
        },
        filled: {
            type: Boolean,
            default: true,
        },
    },

    computed: {
        spinnerClasses() {
            return {
                "ds-c-spinner--filled": this.filled,
                "ds-c-spinner--small": this.size === "small",
                "ds-c-spinner--big": this.size === "large",
            };
        },
    },
};
</script>
