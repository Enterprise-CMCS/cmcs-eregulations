<template>
    <div>
        <span class="test-class">TESTING VITE LIBRARY MODE</span>
        <v-btn depressed> Normal </v-btn>
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
    </div>
</template>

<script>
const SPINNER_SIZES = ["xs", "small", "medium", "large"];

export default {
    name: "TestComponent",

    props: {
        size: {
            validator: (value) => SPINNER_SIZES.includes(value),
            default: "medium",
        },
        filled: {
            type: Boolean,
            default: false,
        },
    },

    computed: {
        spinnerClasses() {
            return {
                "ds-c-spinner--filled": this.filled,
                "ds-c-spinner--small":
                    this.size === "xs" || this.size === "small",
                "ds-c-spinner--big": this.size === "large",
            };
        },

        spinnerStyles() {
            switch (this.size) {
                case "xs":
                    return "margin: 0px";
                case "small":
                    return "margin: 4px";
                default:
                    return "margin: 8px";
            }
        },
    },
};
</script>

<style>
.test-class {
    color: red;
}
</style>
