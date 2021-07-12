<template>
    <div v-bind:class="{ visible: visible }">
        <button v-on:click="click" aria-label="expand or collapse a subpart">
            <slot name="expanded" v-if="visible">Hide</slot>
            <slot name="collapsed" v-if="!visible">Show</slot>
        </button>
    </div>
</template>

<script>
export default {
    name: "collapse-button",

    created: function() {
        this.visible = this.state === "expanded";
        this.$root.$on("collapse-toggle", this.toggle);
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: { //expanded or collapsed
            type: String,
            required: true,
        },
    },

    data: function() {
        return {
            visible: true,
        }
    },

    methods: {
        click: function(event) {
            this.$root.$emit("collapse-toggle", this.name);
        },
        toggle: function(target) {
            if(this.name === target) {
                this.visible = !this.visible;
            }
        },
    },
};
</script>
