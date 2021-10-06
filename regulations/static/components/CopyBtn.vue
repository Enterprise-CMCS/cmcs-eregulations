<template>
    <button
        class="copy-btn"
        :class="classObject"
        :title="title"
        @focus="handleEnter"
        @focusout="handleExit"
        @mouseenter="handleEnter"
        @mouseleave="handleExit"
        @click="handleClick"
    >
        <i class="fa fa-link"></i>
        <span v-if="label">{{ label }}</span>
        <div v-if="entered" class="copy-tooltip hovered">Entered</div>
        <div v-if="clicked" class="copy-tooltip clicked">Clicked</div>
    </button>
</template>

<script>
export default {
    name: "copy-btn",

    props: {
        btn_type: {
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
            entered: false,
            clicked: false,
        };
    },

    computed: {
        classObject: function () {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
    },

    methods: {
        handleEnter(e) {
            if (!this.entered && !this.clicked) this.entered = true;
        },
        handleExit(e) {
            this.entered = false;
        },
        handleClick(e) {
            this.entered = false;
            this.clicked = true;
        },
    },
};
</script>
