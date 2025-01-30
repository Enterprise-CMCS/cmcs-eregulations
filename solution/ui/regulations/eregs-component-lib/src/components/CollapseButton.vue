<template>
    <button
        :class="{ visible: visible }"
        :data-test="dataName"
        :aria-label="visible ? `collapse ${dataName}` : `expand ${dataName}`"
        class="collapsible-title"
        @click="click"
    >
        <slot
            v-if="visible && !keepContentsOnToggle"
            name="expanded"
        >
            Hide
        </slot>
        <slot
            v-if="!visible && !keepContentsOnToggle"
            name="collapsed"
        >
            Show
        </slot>
        <slot v-if="keepContentsOnToggle" name="contents">
            Click here
        </slot>
    </button>
</template>

<script>
import eventbus from "../eventbus";

export default {
    name: "CollapseButton",

    inject: {
        getStateOverride: { default: null },
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: {
            // expanded or collapsed
            type: String,
            required: true,
        },
        keepContentsOnToggle: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    data() {
        return {
            dataName: this.name,
            visible: true,
        };
    },

    computed: {
        stateOverrideValue() {
            if (!this.getStateOverride) return null;
            return this.getStateOverride();
        },
    },

    watch: {
        // https://stackoverflow.com/questions/60416153/making-vue-js-provide-inject-reactive
        stateOverrideValue(newStateOverrideValue) {
            if (this.visible && newStateOverrideValue === "collapsed") {
                this.click();
            } else if (!this.visible && newStateOverrideValue === "expanded") {
                this.click();
            }
        },
    },

    created() {
        this.visible = this.state === "expanded";
        eventbus.on("collapse-toggle", this.toggle);
    },

    beforeUnmount() {
        eventbus.off("collapse-toggle", this.toggle);
    },

    methods: {
        click(event) {
            eventbus.emit("collapse-toggle", this.dataName);
        },
        toggle(target) {
            if (this.dataName === target) {
                this.visible = !this.visible;
            }
        },
    },
};
</script>
