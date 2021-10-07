<template>
    <button
        class="copy-btn"
        :class="classObject"
        :title="title"
        :aria-label="btn_type === 'icon' ? label : false"
        @focus="handleEnter"
        @focusout="handleExit"
        @mouseenter="handleEnter"
        @mouseleave="handleExit"
        @click="handleClick"
    >
        <i class="fa fa-link"></i>
        <span v-if="btn_type === 'labeled-icon'">{{ label }}</span>
        <div
            v-show="entered"
            class="copy-tooltip hovered"
            :style="enteredStyles"
        >
            <p class="hover-msg">{{ label }}</p>
        </div>
    </button>
</template>

<script>
const getAnchorPos = (el, elType) => {
    if (!el) return 0;
    return elType === "labeled-icon"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};
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
    },

    data: function () {
        return {
            entered: false,
            clicked: false,
            leftAnchorPos: undefined,
            label: "Copy Link or Citation",
        };
    },

    computed: {
        classObject() {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
        enteredStyles() {
            return {
                left: this.leftAnchorPos,
                transform: "translate(-50%, 0)",
            };
        },
    },

    methods: {
        handleEnter(e) {
            if (!this.entered && !this.clicked) this.entered = true;
            this.leftAnchorPos = appendPxSuffix(
                getAnchorPos(e.currentTarget, this.btn_type)
            );
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
            this.leftAnchorPos = appendPxSuffix(
                getAnchorPos(e.currentTarget, this.btn_type)
            );
        },
    },
};
</script>
