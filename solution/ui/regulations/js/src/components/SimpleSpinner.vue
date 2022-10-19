<template>
    <div
        :id="boxProperties"
        class="ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center"
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

<script>
export default {
    name: "SimpleSpinner",

    props: {
        size: {
            type: String,
            default: "medium",
        },
        filled: {
            type: Boolean,
            default: false,
        },
        spinnerType: {
            type: String,
            default: ""
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

        spinnerStyles() {
            let pxSize = "8px"
            if (this.spinnerType === "button"){
                pxSize="4px";
            }
            else if(this.size === "small"){
                pxSize= "4px"
            }

            return {
                margin: this.size === pxSize
            };
        },

        boxProperties() {
            return this.spinnerType === "button" ? "fill-center" : ""
        }
    },
};
</script>
<style >
#fill-center{
    width:100%;
}
</style>
