<template>
    <button
        v-bind:class="{ visible: visible }"
        v-bind:data-test="name"
        v-bind:aria-label="visible ? `collapse ${name}` : `expand ${name}`"
        v-on:click="click"
        class="collapsible-title"
    >
        <slot name="expanded" v-if="visible && !keepContentsOnToggle"
            >Hide</slot
        >
        <slot name="collapsed" v-if="!visible && !keepContentsOnToggle"
            >Show</slot
        >
        <slot name="contents" v-if="keepContentsOnToggle">Click here</slot>
    </button>
</template>

<script>
export default {
    name: "collapse-button",

    created: function () {
        this.visible = this.state === "expanded";
        this.$root.$on("collapse-toggle", this.toggle);
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: {
            //expanded or collapsed
            type: String,
            required: true,
        },
        "keep-contents-on-toggle": {
            type: Boolean,
            required: false,
            default: false,
        },
        btnClass: {
            type: String,
            required: false,
        },
    },

    data: function () {
        return {
            name: this.name,
            visible: true,
        };
    },

    methods: {
        click: function (event) {
            this.$root.$emit("collapse-toggle", this.name);
        },
        toggle: function (target) {
            if (this.name === target) {
                this.visible = !this.visible;
            }
        },
    },
};
</script>
