<template>
    <div
        class="ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center"
    >
        <span
            class="ds-c-spinner ds-c-spinner--filled ds-c-spinner--inverse"
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
            default: false,
        },
        inverse: {
            type: Boolean,
            default: false,
        },
    },
};
</script>
