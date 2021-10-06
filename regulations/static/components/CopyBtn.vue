<template>
    <div>
        <div v-if="entered" class="hover-item">Entered</div>
        <div v-if="clicked" class="clicked-item">Clicked</div>
        <button
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
        </button>
    </div>
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
                reference: this.btn_type === "icon",
                "copy-link-btn": this.btn_type === "labeled-icon",
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
