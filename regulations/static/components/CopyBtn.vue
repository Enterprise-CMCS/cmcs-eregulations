<template>
    <button
        :class="[className]"
        :title="title"
        @focusin="handleFocusIn()"
        @focusout="handleFocusOut()"
        @mouseenter="handleMouseEnter()"
        @mouseleave="handleMouseLeave()"
        @click="handleClick()"
    >
        <i class="fa fa-link"></i>
        <span v-if="label">{{ label }}</span>
    </button>
</template>

<script>
export default {
    name: "copy-btn",

    props: {
        class: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        label: String,
    },

    data: function () {
        return {
            className: this.class,
            title: this.title,
        };
    },

    methods: {
        handleFocusIn() {
            console.log("focused!");
        },
        handleFocusOut() {
            console.log("unfocused!");
        },
        handleMouseEnter() {
            // state change
            console.log("mouse entered!");
        },
        handleMouseLeave() {
            // state change
            console.log("mouse left!");
        },
        handleClick() {
            // state change
            console.log("clicked!");
        },
    },
};
</script>
