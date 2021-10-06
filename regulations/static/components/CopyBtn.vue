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
        <div v-show="entered" class="copy-tooltip hovered" :style="styleObject">
            Entered
        </div>
    </button>
</template>

<script>
const appendPxSuffix = (int) => `${int}px`;

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
            leftAnchorPos: undefined,
        };
    },

    computed: {
        classObject: function () {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
        styleObject: function () {
            return {
                left: this.leftAnchorPos,
                transform: "translate(-50%, 0)",
            };
        },
    },

    methods: {
        handleEnter(e) {
            if (!this.entered && !this.clicked) this.entered = true;
            this.leftAnchorPos = appendPxSuffix(e.currentTarget.offsetWidth / 2);
        },
        handleExit(e) {
            if (!this.clicked) {
                this.entered = false;
                this.leftAnchorPos = undefined;
            }
        },
        handleClick(e) {
            this.entered = false;
            this.clicked = true;
            this.leftAnchorPos = appendPxSuffix(e.currentTarget.offsetWidth / 2);
        },
    },
};
</script>
