<template>
    <div
        ref="target"
        v-bind:class="{ visible: visible }"
        v-bind:style="[styles, sizeStyle]"
    >
        <slot></slot>
    </div>
</template>

<script>
export default {
    name: "collapsible",

    created: function () {
        this.visible = this.state === "expanded";
        this.isVertical = this.direction === "vertical";
        this.$root.$on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
    },

    destroyed: function () {
        window.removeEventListener("resize", this.resize);
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
        transition: {
            type: String,
            required: false,
            default: "1s",
        },
        direction: {
            //horizontal or vertical
            type: String,
            required: true,
        },
    },

    data: function () {
        return {
            size: 0,
            visible: true,
            isVertical: true,
            styles: {
                overflow: "hidden",
                transition: this.transition,
            },
        };
    },

    computed: {
        sizeStyle: function () {
            return this.isVertical
                ? { height: this.visible ? this.size : 0 }
                : { width: this.visible ? this.size : 0 };
        },
    },

    methods: {
        resize: function (e) {
            this.computeSize();
        },
        toggle: function (target) {
            if (this.name === target) {
                if (!this.visible) {
                    this.computeSize();
                }
                requestAnimationFrame(() => {
                    this.visible = !this.visible;
                });
            }
        },
        getStyle: function () {
            return window.getComputedStyle(this.$refs.target);
        },
        setProps: function (visibility, display, position, size) {
            this.$refs.target.style.visibility = visibility;
            this.$refs.target.style.display = display;
            this.$refs.target.style.position = position;
            if (this.isVertical) {
                this.$refs.target.style.height = size;
            } else {
                this.$refs.target.style.width = size;
            }
        },
        computeSize: function () {
            const prevSize = this.isVertical
                ? this.getStyle().height
                : this.getStyle().width;

            this.setProps("hidden", "block", "absolute", "auto");

            this.size = this.isVertical
                ? this.getStyle().height
                : this.getStyle().width;

            this.setProps(null, null, null, prevSize);
        },
    },
};
</script>
